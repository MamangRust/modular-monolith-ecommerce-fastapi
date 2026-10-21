"""Unit tests for the cart services (no DB/Redis). Covers the cache-first query service (window `total_count` from the first row) and the command service: - `create` resolves the product through the adapter first, then applies the two inline business rules (`quantity <= 0` -> `err_cart_quantity_zero`, `count_in_stock < quantity` -> `err_cart_insufficient_stock`), validates the owner through the user adapter, snapshots the product fields, and evicts the user's cached listings; - `delete_permanent`/`delete_all` hard-delete and evict; - every adapter/repository failure propagates unchanged (`HandleError`), so no method substitutes a service sentinel."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any

import pytest

from pkg.database.schema.cart import CartRow, GetCartsRow
from pkg.database.schema.product import GetProductByIDRow
from pkg.logger.logger import Logger
from service.cart.service.cart_command_service import CartCommandServiceImpl
from service.cart.service.cart_query_service import CartQueryServiceImpl
from shared.domain.requests.cart import (
    CreateCartRequest,
    DeleteAllCartRequest,
    DeleteCartRequest,
    FindAllCarts,
)
from shared.errors import (
    AppError,
    err_cart_insufficient_stock,
    err_cart_quantity_zero,
    err_product_not_found,
    err_user_not_found_repo,
)
from shared.observability import Observability

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)


def _logger() -> Logger:
    return Logger("test", "error")


def _obs() -> Observability:
    return Observability("test", _logger())


# ---- query service ----


def _list_row(cart_id: int = 1, total: int = 11) -> GetCartsRow:
    return GetCartsRow(
        cart_id=cart_id,
        user_id=5,
        product_id=10,
        name="Galaxy S24",
        price=1200,
        image="galaxy-s24.jpg",
        quantity=2,
        weight=200,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


class FakeQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_all(self, request: FindAllCarts) -> list[GetCartsRow]:
        self.calls.append(f"find_all:{request.user_id}:{request.page}:{request.page_size}")
        return [_list_row()]


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_carts(self, request: FindAllCarts):
        return self.store.get(f"{request.user_id}:{request.page}:{request.page_size}:{request.search}")

    async def set_carts(self, request: FindAllCarts, rows, total):
        key = f"{request.user_id}:{request.page}:{request.page_size}:{request.search}"
        self.writes.append(key)
        self.store[key] = (rows, total)


def _query_service(
    repo: FakeQueryRepo, cache: FakeQueryCache
) -> CartQueryServiceImpl:
    return CartQueryServiceImpl(repo, cache, _logger(), _obs())


async def test_query_find_all_caches_and_serves_cache_first() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    rows, total = await service.find_all(FindAllCarts(user_id=5, page=1, page_size=10, search=""))
    assert total == 11
    assert cache.writes == ["5:1:10:"]
    repo.calls.clear()

    cached_rows, _ = await service.find_all(FindAllCarts(user_id=5, page=1, page_size=10, search=""))
    assert repo.calls == []
    assert cached_rows[0].cart_id == rows[0].cart_id


async def test_query_empty_page_reports_zero_total() -> None:
    class EmptyRepo(FakeQueryRepo):
        async def find_all(self, request):
            return []

    rows, total = await _query_service(EmptyRepo(), FakeQueryCache()).find_all(
        FindAllCarts(user_id=5, page=1, page_size=10, search="")
    )
    assert rows == []
    assert total == 0


async def test_query_total_comes_from_window_count() -> None:
    class BigRepo(FakeQueryRepo):
        async def find_all(self, request):
            return [_list_row(1, total=42), _list_row(2, total=42)]

    rows, total = await _query_service(BigRepo(), FakeQueryCache()).find_all(
        FindAllCarts(user_id=5, page=1, page_size=10, search="")
    )
    assert len(rows) == 2
    assert total == 42


async def test_query_errors_propagate_unchanged() -> None:
    class FailingRepo(FakeQueryRepo):
        async def find_all(self, request):
            raise AppError("INTERNAL", 500, "boom")

    with pytest.raises(AppError) as excinfo:
        await _query_service(FailingRepo(), FakeQueryCache()).find_all(
            FindAllCarts(user_id=5, page=1, page_size=10, search="")
        )
    assert excinfo.value.code == 500
    assert excinfo.value.message == "boom"


# ---- command service ----


def _product_row(**overrides: Any) -> GetProductByIDRow:
    base = GetProductByIDRow(
        product_id=10,
        merchant_id=3,
        category_id=2,
        name="Galaxy S24",
        description="desc",
        price=1200,
        count_in_stock=5,
        brand="Samsung",
        weight=200,
        rating=4.5,
        slug_product="galaxy-s24",
        image_product="galaxy-s24.jpg",
        created_at=CREATED,
        updated_at=UPDATED,
    )
    return replace(base, **overrides)


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request) -> CartRow:
        self.calls.append(
            f"create:{request.product_id}:{request.user_id}:{request.quantity}"
        )
        return CartRow(
            cart_id=9,
            user_id=request.user_id,
            product_id=request.product_id,
            name=request.name,
            price=request.price,
            image=request.image_product,
            quantity=request.quantity,
            weight=request.weight,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def delete_permanent(self, request) -> bool:
        self.calls.append(f"delete:{request.cart_id}:{request.user_id}")
        return True

    async def delete_all_permanently(self, request) -> bool:
        self.calls.append(f"delete_all:{request.user_id}:{len(request.cart_ids)}")
        return True


class FakeCommandCache:
    def __init__(self) -> None:
        self.evicted: list[int] = []

    async def delete_cached_carts(self, user_id: int) -> int:
        self.evicted.append(user_id)
        return 1


class FakeProductAdapter:
    def __init__(self, row: Any = None) -> None:
        self.row = row or _product_row()
        self.calls: list[int] = []

    async def find_by_id(self, product_id: int) -> Any:
        self.calls.append(product_id)
        return self.row


class FakeUserAdapter:
    def __init__(self, error: AppError | None = None) -> None:
        self.error = error
        self.calls: list[int] = []

    async def find_by_id(self, user_id: int) -> Any:
        self.calls.append(user_id)
        if self.error is not None:
            raise self.error
        return object()


def _command_service(
    repo: FakeCommandRepo,
    cache: FakeCommandCache,
    product: Any = None,
    user: Any = None,
) -> CartCommandServiceImpl:
    return CartCommandServiceImpl(
        repo,
        product or FakeProductAdapter(),
        user or FakeUserAdapter(),
        cache,
        _logger(),
        _obs(),
    )


def _create_request(**overrides: Any) -> CreateCartRequest:
    values = {"product_id": 10, "user_id": 5, "quantity": 2}
    values.update(overrides)
    return CreateCartRequest(**values)


async def test_command_create_snapshots_product_and_evicts() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    product, user = FakeProductAdapter(), FakeUserAdapter()
    service = _command_service(repo, cache, product=product, user=user)

    cart = await service.create(_create_request(product_id=10, user_id=5, quantity=2))
    assert product.calls == [10]
    assert user.calls == [5]
    assert repo.calls == ["create:10:5:2"]
    assert cart.cart_id == 9
    assert cart.name == "Galaxy S24"
    assert cart.price == 1200
    assert cart.image == "galaxy-s24.jpg"
    assert cart.weight == 200
    assert cache.evicted == [5]


async def test_command_create_null_image_and_weight_become_zero_values() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    product = FakeProductAdapter(_product_row(image_product=None, weight=None))
    service = _command_service(repo, cache, product=product)

    cart = await service.create(_create_request())
    assert cart.image == ""
    assert cart.weight == 0


async def test_command_create_quantity_guard() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    product = FakeProductAdapter()
    service = _command_service(repo, cache, product=product)

    # The pydantic DTO forbids quantity < 1, so build an invalid instance the
    # way the service would observe one.
    invalid = CreateCartRequest.model_construct(product_id=10, user_id=5, quantity=0)
    with pytest.raises(AppError) as excinfo:
        await service.create(invalid)
    assert excinfo.value is err_cart_quantity_zero
    # Product resolved first, but no user lookup / write / eviction happened.
    assert product.calls == [10]
    assert repo.calls == []
    assert cache.evicted == []


async def test_command_create_insufficient_stock_guard() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    product = FakeProductAdapter(_product_row(count_in_stock=1))
    user = FakeUserAdapter()
    service = _command_service(repo, cache, product=product, user=user)

    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request(quantity=2))
    assert excinfo.value is err_cart_insufficient_stock
    assert user.calls == []
    assert repo.calls == []
    assert cache.evicted == []


async def test_command_create_propagates_adapter_errors() -> None:
    class FailingProduct(FakeProductAdapter):
        async def find_by_id(self, product_id):
            raise err_product_not_found

    service = _command_service(
        FakeCommandRepo(), FakeCommandCache(), product=FailingProduct()
    )
    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request())
    assert excinfo.value is err_product_not_found

    service = _command_service(
        FakeCommandRepo(),
        FakeCommandCache(),
        user=FakeUserAdapter(error=err_user_not_found_repo),
    )
    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request())
    assert excinfo.value is err_user_not_found_repo


async def test_command_delete_permanent_and_all_evict() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    deleted = await service.delete_permanent(DeleteCartRequest(cart_id=3, user_id=5))
    assert deleted is True
    assert repo.calls == ["delete:3:5"]
    assert cache.evicted == [5]

    deleted_all = await service.delete_all(
        DeleteAllCartRequest(user_id=5, cart_ids=[3, 4])
    )
    assert deleted_all is True
    assert repo.calls[-1] == "delete_all:5:2"
    assert cache.evicted == [5, 5]


async def test_command_errors_propagate_unchanged() -> None:
    class FailingRepo(FakeCommandRepo):
        async def create(self, request):
            raise AppError("INTERNAL", 500, "failed to create cart")

        async def delete_permanent(self, request):
            raise AppError("INTERNAL", 500, "failed to permanently delete cart")

        async def delete_all_permanently(self, request):
            raise AppError("INTERNAL", 500, "failed to permanently delete all carts")

    service = _command_service(FailingRepo(), FakeCommandCache())

    with pytest.raises(AppError) as create_exc:
        await service.create(_create_request())
    assert create_exc.value.message == "failed to create cart"

    with pytest.raises(AppError) as delete_exc:
        await service.delete_permanent(DeleteCartRequest(cart_id=1, user_id=5))
    assert delete_exc.value.message == "failed to permanently delete cart"

    with pytest.raises(AppError) as all_exc:
        await service.delete_all(DeleteAllCartRequest(user_id=5, cart_ids=[1]))
    assert all_exc.value.message == "failed to permanently delete all carts"


__all__ = []
