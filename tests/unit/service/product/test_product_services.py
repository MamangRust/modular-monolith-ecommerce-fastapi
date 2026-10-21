"""Unit tests for the product services (no DB/Redis). Covers the cache-first query service (window `total_count` from the first row) and the command service. Error: the product service forwards repository errors unchanged through `HandleError`/`HandlerErrorPagination`, so read/write failures keep the repository sentinel (e.g. 404 `product not found`). Only three sentinels are substituted by the service: - `update_product_count_stock`: guard `product_id <= 0 || stock < 0` -> `err_failed_count_stock` (500 "Failed to count stock"); - `adjust_product_stock`: guard `product_id <= 0 || delta == 0 || operation_id == ""` -> the same sentinel; - `delete_all`: any repository failure -> `err_failed_delete_all_products_permanent`. `create`/`update` validate the parent category then merchant through the gRPC adapters (adapter errors propagate unchanged), derive the slug, and evict the `product:*` namespace. `restore_all`/`delete_all` do NOT evict."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from pkg.database.schema.product import (
    AdjustProductStockRow,
    CreateProductRow,
    GetProductByIDRow,
    GetProductsActiveRow,
    GetProductsByMerchantRow,
    GetProductsRow,
    Product,
    UpdateProductRow,
)
from pkg.logger.logger import Logger
from service.product.service.product_command_service import (
    ProductCommandServiceImpl,
)
from service.product.service.product_query_service import (
    ProductQueryServiceImpl,
)
from shared.domain.requests.product import (
    CreateProductRequest,
    UpdateProductRequest,
)
from shared.errors import (
    AppError,
    err_failed_count_stock,
    err_failed_delete_all_products_permanent,
    err_failed_delete_image_product,
    err_merchant_internal,
)
from shared.errors.category_errors import err_find_category_by_id
from shared.observability import Observability

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 5, 6, 7)


def _logger() -> Logger:
    return Logger("test", "error")


def _obs() -> Observability:
    return Observability("test", _logger())


# ---- query service ----


def _list_row(product_id: int = 1, total: int = 11) -> GetProductsRow:
    return GetProductsRow(
        product_id=product_id,
        merchant_id=10,
        category_id=3,
        name="Smartphone Galaxy X",
        description="desc",
        price=4500000,
        count_in_stock=20,
        brand="Samsung",
        weight=300,
        rating=4.5,
        slug_product="smartphone-galaxy-x",
        image_product="galaxy-x.jpg",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(
    product_id: int = 1, deleted_at: datetime | None = None
) -> GetProductsActiveRow:
    return GetProductsActiveRow(
        product_id=product_id,
        merchant_id=10,
        category_id=3,
        name="Smartphone Galaxy X",
        description="desc",
        price=4500000,
        count_in_stock=20,
        brand="Samsung",
        weight=300,
        rating=4.5,
        slug_product="smartphone-galaxy-x",
        image_product="galaxy-x.jpg",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=1,
    )


def _merchant_row(product_id: int = 1) -> GetProductsByMerchantRow:
    return GetProductsByMerchantRow(
        product_id=product_id,
        merchant_id=10,
        category_id=3,
        name="Smartphone Galaxy X",
        description="desc",
        price=4500000,
        count_in_stock=20,
        brand="Samsung",
        weight=300,
        rating=4.5,
        slug_product="smartphone-galaxy-x",
        image_product="galaxy-x.jpg",
        created_at=CREATED,
        updated_at=UPDATED,
        category_name="Elektronik",
        total_count=1,
    )


def _by_id_row(product_id: int = 1) -> GetProductByIDRow:
    return GetProductByIDRow(
        product_id=product_id,
        merchant_id=10,
        category_id=3,
        name="Smartphone Galaxy X",
        description="desc",
        price=4500000,
        count_in_stock=20,
        brand="Samsung",
        weight=300,
        rating=4.5,
        slug_product="smartphone-galaxy-x",
        image_product="galaxy-x.jpg",
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_all(self, search, page, page_size):
        self.calls.append(f"find_all:{search}:{page}:{page_size}")
        return [_list_row()]

    async def find_active(self, search, page, page_size):
        self.calls.append("find_active")
        return [_active_row()]

    async def find_trashed(self, search, page, page_size):
        self.calls.append("find_trashed")
        return [_active_row(deleted_at=DELETED)]

    async def find_by_merchant(self, merchant_id, category_id, search, min_price, max_price, page, page_size):
        self.calls.append(f"find_by_merchant:{merchant_id}:{category_id}")
        return [_merchant_row()]

    async def find_by_category(self, category_name, search, min_price, max_price, page, page_size):
        self.calls.append(f"find_by_category:{category_name}")
        return [_merchant_row()]

    async def find_by_id(self, product_id):
        self.calls.append(f"find_by_id:{product_id}")
        return _by_id_row(product_id)

    async def find_by_id_trashed(self, product_id):
        self.calls.append(f"find_by_id_trashed:{product_id}")
        return Product(
            product_id=product_id,
            merchant_id=10,
            category_id=3,
            name="Smartphone Galaxy X",
            description="desc",
            price=4500000,
            count_in_stock=20,
            brand="Samsung",
            weight=300,
            rating=4.5,
            slug_product="smartphone-galaxy-x",
            image_product="",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_products(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_products(self, page, page_size, search, rows, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (rows, total)

    async def get_products_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_products_active(self, page, page_size, search, rows, total):
        self.store[f"active:{page}:{page_size}:{search}"] = (rows, total)

    async def get_products_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_products_trashed(self, page, page_size, search, rows, total):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (rows, total)

    async def get_products_by_merchant(self, merchant_id, category_id, min_price, max_price, page, page_size, search):
        return self.store.get(f"merchant:{merchant_id}:{page}:{page_size}:{search}")

    async def set_products_by_merchant(self, merchant_id, category_id, min_price, max_price, page, page_size, search, rows, total):
        self.store[f"merchant:{merchant_id}:{page}:{page_size}:{search}"] = (rows, total)

    async def get_products_by_category(self, category_name, min_price, max_price, page, page_size, search):
        return self.store.get(f"category:{category_name}:{page}:{page_size}:{search}")

    async def set_products_by_category(self, category_name, min_price, max_price, page, page_size, search, rows, total):
        self.store[f"category:{category_name}:{page}:{page_size}:{search}"] = (rows, total)

    async def get_product(self, product_id):
        return self.store.get(f"id:{product_id}")

    async def set_product(self, row):
        self.writes.append(f"id:{row.product_id}")
        self.store[f"id:{row.product_id}"] = row


def _query_service(
    repo: FakeQueryRepo, cache: FakeQueryCache
) -> ProductQueryServiceImpl:
    return ProductQueryServiceImpl(repo, cache, _logger(), _obs())


async def test_query_find_all_caches_and_serves_cache_first() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    rows, total = await service.find_all("", 1, 10)
    assert total == 11
    assert cache.writes == ["all:1:10:"]
    repo.calls.clear()

    cached_rows, _ = await service.find_all("", 1, 10)
    assert repo.calls == []
    assert cached_rows[0].product_id == rows[0].product_id


async def test_query_active_trashed_merchant_category_cache() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    await service.find_active("", 1, 10)
    await service.find_trashed("", 1, 10)
    await service.find_by_merchant(10, 3, "", 0, 0, 1, 10)
    await service.find_by_category("Elektronik", "", 0, 0, 1, 10)
    assert repo.calls == [
        "find_active",
        "find_trashed",
        "find_by_merchant:10:3",
        "find_by_category:Elektronik",
    ]

    repo.calls.clear()
    await service.find_active("", 1, 10)
    await service.find_trashed("", 1, 10)
    await service.find_by_merchant(10, 3, "", 0, 0, 1, 10)
    await service.find_by_category("Elektronik", "", 0, 0, 1, 10)
    assert repo.calls == []


async def test_query_find_by_id_caches() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    await service.find_by_id(5)
    assert repo.calls == ["find_by_id:5"]
    assert cache.writes == ["id:5"]


async def test_query_empty_page_reports_zero_total() -> None:
    class EmptyRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            return []

    rows, total = await _query_service(EmptyRepo(), FakeQueryCache()).find_all(
        "", 1, 10
    )
    assert rows == []
    assert total == 0


async def test_query_total_comes_from_window_count() -> None:
    class BigRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            return [_list_row(1, total=42), _list_row(2, total=42)]

    rows, total = await _query_service(BigRepo(), FakeQueryCache()).find_all(
        "", 1, 10
    )
    assert len(rows) == 2
    assert total == 42


async def test_query_errors_propagate_unchanged() -> None:
    class FailingRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            raise AppError("INTERNAL", 500, "boom")

        async def find_by_id(self, product_id):
            raise AppError("NOT_FOUND", 404, "product not found")

    service = _query_service(FailingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as all_exc:
        await service.find_all("", 1, 10)
    assert all_exc.value.code == 500
    assert all_exc.value.message == "boom"

    with pytest.raises(AppError) as by_id_exc:
        await service.find_by_id(1)
    assert by_id_exc.value.code == 404
    assert by_id_exc.value.message == "product not found"


# ---- command service ----


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request):
        self.calls.append(f"create:{request.name}:{request.slug_product}")
        return CreateProductRow(
            product_id=9,
            merchant_id=request.merchant_id,
            category_id=request.category_id,
            name=request.name,
            description=request.description,
            price=request.price,
            count_in_stock=request.count_in_stock,
            brand=request.brand,
            weight=request.weight,
            rating=float(request.rating),
            slug_product=request.slug_product,
            image_product=request.image_product,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.product_id}:{request.slug_product}")
        return UpdateProductRow(
            product_id=request.product_id or 1,
            merchant_id=request.merchant_id,
            category_id=request.category_id,
            name=request.name,
            description=request.description,
            price=request.price,
            count_in_stock=request.count_in_stock,
            brand=request.brand,
            weight=request.weight,
            rating=float(request.rating),
            slug_product=request.slug_product,
            image_product=request.image_product,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update_product_count_stock(self, product_id, stock):
        self.calls.append(f"count_stock:{product_id}:{stock}")
        return AdjustProductStockRow(product_id=product_id, count_in_stock=stock)

    async def adjust_product_stock(self, product_id, delta, operation_id):
        self.calls.append(f"adjust:{product_id}:{delta}:{operation_id}")
        return AdjustProductStockRow(product_id=product_id, count_in_stock=8)

    async def trash(self, product_id):
        self.calls.append(f"trash:{product_id}")
        return Product(
            product_id=product_id,
            merchant_id=10,
            category_id=3,
            name="P",
            description="d",
            price=1,
            count_in_stock=1,
            brand="b",
            weight=1,
            rating=4.5,
            slug_product="p",
            image_product="",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, product_id):
        self.calls.append(f"restore:{product_id}")
        return Product(
            product_id=product_id,
            merchant_id=10,
            category_id=3,
            name="P",
            description="d",
            price=1,
            count_in_stock=1,
            brand="b",
            weight=1,
            rating=4.5,
            slug_product="p",
            image_product="",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, product_id):
        self.calls.append(f"delete:{product_id}")
        return True

    async def restore_all(self):
        self.calls.append("restore_all")
        return True

    async def delete_all(self):
        self.calls.append("delete_all")
        return True


class FakeCommandCache:
    def __init__(self) -> None:
        self.evicted: list[int] = []

    async def delete_cached_product(self, product_id: int) -> int:
        self.evicted.append(product_id)
        return 1


class FakeAdapter:
    def __init__(self, name: str) -> None:
        self.name = name
        self.calls: list[int] = []

    async def find_by_id(self, entity_id: int) -> Any:
        self.calls.append(entity_id)
        return object()


class FailingAdapter:
    def __init__(self, error: AppError) -> None:
        self._error = error

    async def find_by_id(self, entity_id: int) -> Any:
        raise self._error


def _command_service(
    repo: FakeCommandRepo,
    cache: FakeCommandCache,
    query_repo: FakeQueryRepo | None = None,
    category: Any = None,
    merchant: Any = None,
) -> ProductCommandServiceImpl:
    return ProductCommandServiceImpl(
        repo,
        query_repo or FakeQueryRepo(),
        category or FakeAdapter("category"),
        merchant or FakeAdapter("merchant"),
        cache,
        _logger(),
        _obs(),
    )


def _create_request(**overrides: Any) -> CreateProductRequest:
    values = {
        "merchant_id": 10,
        "category_id": 3,
        "name": "Smartphone Galaxy X",
        "description": "desc",
        "price": 4500000,
        "count_in_stock": 20,
        "brand": "Samsung",
        "weight": 300,
        "rating": 4,
        "image_product": "galaxy-x.jpg",
    }
    values.update(overrides)
    return CreateProductRequest(**values)


def _update_request(product_id: int = 4, **overrides: Any) -> UpdateProductRequest:
    values = {
        "product_id": product_id,
        "merchant_id": 10,
        "category_id": 3,
        "name": "Smartphone Galaxy X",
        "description": "desc",
        "price": 4500000,
        "count_in_stock": 20,
        "brand": "Samsung",
        "weight": 300,
        "rating": 4,
        "image_product": "galaxy-x.jpg",
    }
    values.update(overrides)
    return UpdateProductRequest(**values)


async def test_command_create_validates_parents_slugs_and_evicts() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    category, merchant = FakeAdapter("category"), FakeAdapter("merchant")
    service = _command_service(repo, cache, category=category, merchant=merchant)

    row = await service.create(_create_request(merchant_id=7, category_id=2))
    assert row.product_id == 9
    # category validated before merchant
    assert category.calls == [2]
    assert merchant.calls == [7]
    assert repo.calls and repo.calls[0].startswith("create:Smartphone Galaxy X:")
    assert cache.evicted == [9]


async def test_command_create_propagates_adapter_error() -> None:
    service = _command_service(
        FakeCommandRepo(),
        FakeCommandCache(),
        category=FailingAdapter(err_find_category_by_id),
    )
    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request())
    assert excinfo.value is err_find_category_by_id

    service = _command_service(
        FakeCommandRepo(),
        FakeCommandCache(),
        merchant=FailingAdapter(err_merchant_internal),
    )
    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request())
    assert excinfo.value is err_merchant_internal


async def test_command_update_validates_slugs_and_evicts() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    row = await service.update(_update_request(4))
    assert row.product_id == 4
    assert row.slug_product is not None
    assert row.slug_product.startswith("smartphone-galaxy-x-")
    assert cache.evicted == [4]


async def test_command_count_stock_guard_and_evict() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    row = await service.update_product_count_stock(5, 12)
    assert row.count_in_stock == 12
    assert cache.evicted == [5]

    for pid, stock in ((0, 5), (-1, 5), (5, -1)):
        with pytest.raises(AppError) as excinfo:
            await service.update_product_count_stock(pid, stock)
        assert excinfo.value is err_failed_count_stock


async def test_command_adjust_stock_guard_and_evict() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    row = await service.adjust_product_stock(5, 3, "op-1")
    assert row.count_in_stock == 8
    assert cache.evicted == [5]

    for pid, delta, op in ((0, 3, "op"), (5, 0, "op"), (5, 3, "")):
        with pytest.raises(AppError) as excinfo:
            await service.adjust_product_stock(pid, delta, op)
        assert excinfo.value is err_failed_count_stock


async def test_command_trash_restore_delete_propagate_and_evict() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.trash(3)
    await service.restore(3)
    assert cache.evicted == [3, 3]

    class FailingRepo(FakeCommandRepo):
        async def trash(self, product_id):
            raise AppError("NOT_FOUND", 404, "gone")

        async def restore(self, product_id):
            raise AppError("NOT_FOUND", 404, "gone")

    failing = _command_service(FailingRepo(), FakeCommandCache())
    for call in (failing.trash(1), failing.restore(1)):
        with pytest.raises(AppError) as excinfo:
            await call
        assert excinfo.value.code == 404
        assert excinfo.value.message == "gone"


async def test_command_delete_permanent_removes_image_and_evicts(tmp_path) -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    image = tmp_path / "galaxy-x.jpg"
    image.write_bytes(b"img")

    query_repo = FakeQueryRepo()

    async def _with_image(product_id):
        return Product(
            product_id=product_id,
            merchant_id=10,
            category_id=3,
            name="P",
            description="d",
            price=1,
            count_in_stock=1,
            brand="b",
            weight=1,
            rating=4.5,
            slug_product="p",
            image_product=str(image),
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    query_repo.find_by_id_trashed = _with_image  # type: ignore[method-assign]
    service = _command_service(repo, cache, query_repo=query_repo)

    assert await service.delete_permanent(3) is True
    assert not image.exists()
    assert cache.evicted == [3]

    # A missing image file is ignored (`os.IsNotExist`).
    await service.delete_permanent(4)
    assert cache.evicted == [3, 4]


async def test_command_delete_permanent_image_error(tmp_path) -> None:
    query_repo = FakeQueryRepo()

    async def _bad_image(product_id):
        row = await FakeQueryRepo().find_by_id_trashed(product_id)
        # A directory makes `os.remove` raise a non-`FileNotFoundError` OSError.
        row.image_product = str(tmp_path)
        return row

    query_repo.find_by_id_trashed = _bad_image  # type: ignore[method-assign]
    service = _command_service(FakeCommandRepo(), FakeCommandCache(), query_repo=query_repo)
    with pytest.raises(AppError) as excinfo:
        await service.delete_permanent(3)
    assert excinfo.value.is_(err_failed_delete_image_product)


async def test_command_restore_all_propagates_and_delete_all_remaps() -> None:
    class FailingRepo(FakeCommandRepo):
        async def restore_all(self):
            raise AppError("INTERNAL", 500, "boom")

        async def delete_all(self):
            raise AppError("CONFLICT", 409, "fk")

    cache = FakeCommandCache()
    service = _command_service(FailingRepo(), cache)

    with pytest.raises(AppError) as restore_exc:
        await service.restore_all()
    assert restore_exc.value.code == 500
    assert restore_exc.value.message == "boom"

    with pytest.raises(AppError) as delete_exc:
        await service.delete_all()
    assert delete_exc.value.is_(err_failed_delete_all_products_permanent)
    assert delete_exc.value.internal is not None
    # Bulk operations do not evict.
    assert cache.evicted == []


__all__ = []
