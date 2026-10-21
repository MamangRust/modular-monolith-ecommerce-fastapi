"""Unit tests for the review services (no DB/Redis). Covers the cache-first query service and the command service: - the five list reads take the window `total_count` from the first row (0 when empty) and substitute the *service* sentinel on repository failure (`err_failed_find_all_reviews` etc.) — unlike product/cart, whose services propagate the repository error; - `find_by_id` wraps any repository failure as `err_review_not_found` (reuses the repository sentinel here); - `create` validates the user first, then the product, writes with an empty `name` (request has none), and evicts the cache; - `update` pre-loads the review (missing -> `err_review_not_found`), then writes (`err_failed_update_review` on failure) and evicts; - `trash`/`restore`/`delete_permanent`/`delete_all` propagate repository errors unchanged; `restore_all` substitutes `err_failed_restore_all_reviews`."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any

import pytest

from pkg.database.schema.product import GetProductByIDRow
from pkg.database.schema.review import (
    GetReviewByIDRow,
    GetReviewByProductIdRow,
    GetReviewsActiveRow,
    GetReviewsRow,
    Review,
    ReviewRow,
)
from pkg.logger.logger import Logger
from service.review.service.review_command_service import ReviewCommandServiceImpl
from service.review.service.review_query_service import ReviewQueryServiceImpl
from shared.domain.requests.review import (
    CreateReviewRecord,
    CreateReviewRequest,
    FindAllReviews,
    FindAllReviewsByMerchant,
    FindAllReviewsByProduct,
    UpdateReviewRequest,
)
from shared.errors import (
    AppError,
    err_failed_create_review,
    err_failed_find_active_reviews,
    err_failed_find_all_reviews,
    err_failed_find_by_merchant_reviews,
    err_failed_find_by_product_reviews,
    err_failed_find_trashed_reviews,
    err_failed_restore_all_reviews,
    err_failed_update_review,
    err_product_not_found,
    err_review_not_found,
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


def _list_row(review_id: int = 1, total: int = 11) -> GetReviewsRow:
    return GetReviewsRow(
        review_id=review_id,
        user_id=5,
        product_id=10,
        name="John",
        comment="Produk bagus!",
        rating=5,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(review_id: int = 1, total: int = 11) -> GetReviewsActiveRow:
    return GetReviewsActiveRow(
        review_id=review_id,
        user_id=5,
        product_id=10,
        name="John",
        comment="Produk bagus!",
        rating=5,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=total,
    )


def _detail_row(review_id: int = 1, total: int = 11) -> GetReviewByProductIdRow:
    return GetReviewByProductIdRow(
        review_id=review_id,
        user_id=5,
        product_id=10,
        name="John",
        comment="Produk bagus!",
        rating=5,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=total,
        review_details=None,
    )


class FakeQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_all(self, request: FindAllReviews) -> list[GetReviewsRow]:
        self.calls.append(f"find_all:{request.page}:{request.page_size}")
        return [_list_row()]

    async def find_by_product(
        self, request: FindAllReviewsByProduct
    ) -> list[GetReviewByProductIdRow]:
        self.calls.append(f"find_by_product:{request.product_id}")
        return [_detail_row()]

    async def find_by_merchant(
        self, request: FindAllReviewsByMerchant
    ) -> list[GetReviewByProductIdRow]:
        self.calls.append(f"find_by_merchant:{request.merchant_id}")
        return [_detail_row()]

    async def find_active(self, request: FindAllReviews) -> list[GetReviewsActiveRow]:
        self.calls.append("find_active")
        return [_active_row()]

    async def find_trashed(self, request: FindAllReviews) -> list[GetReviewsActiveRow]:
        self.calls.append("find_trashed")
        return [_active_row()]

    async def find_by_id(self, review_id: int) -> GetReviewByIDRow:
        self.calls.append(f"find_by_id:{review_id}")
        return ReviewRow(
            review_id=review_id,
            user_id=5,
            product_id=10,
            name="John",
            comment="Produk bagus!",
            rating=5,
            created_at=CREATED,
            updated_at=UPDATED,
        )


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_all(self, request):
        return self.store.get(f"all:{request.page}:{request.page_size}:{request.search}")

    async def set_all(self, request, rows, total):
        key = f"all:{request.page}:{request.page_size}:{request.search}"
        self.writes.append(key)
        self.store[key] = (rows, total)

    async def get_by_product(self, request):
        return self.store.get(f"prod:{request.product_id}")

    async def set_by_product(self, request, rows, total):
        self.writes.append(f"prod:{request.product_id}")
        self.store[f"prod:{request.product_id}"] = (rows, total)

    async def get_by_merchant(self, request):
        return self.store.get(f"mer:{request.merchant_id}")

    async def set_by_merchant(self, request, rows, total):
        self.writes.append(f"mer:{request.merchant_id}")
        self.store[f"mer:{request.merchant_id}"] = (rows, total)

    async def get_active(self, request):
        return self.store.get("active")

    async def set_active(self, request, rows, total):
        self.writes.append("active")
        self.store["active"] = (rows, total)

    async def get_trashed(self, request):
        return self.store.get("trashed")

    async def set_trashed(self, request, rows, total):
        self.writes.append("trashed")
        self.store["trashed"] = (rows, total)

    async def get_by_id(self, review_id: int):
        return self.store.get(f"id:{review_id}")

    async def set_by_id(self, row):
        self.writes.append(f"id:{row.review_id}")
        self.store[f"id:{row.review_id}"] = row


def _query_service(
    repo: FakeQueryRepo, cache: FakeQueryCache
) -> ReviewQueryServiceImpl:
    return ReviewQueryServiceImpl(repo, cache, _logger(), _obs())


async def test_query_find_all_caches_and_serves_cache_first() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    rows, total = await service.find_all(
        FindAllReviews(search="", page=1, page_size=10)
    )
    assert total == 11
    assert cache.writes == ["all:1:10:"]
    repo.calls.clear()

    cached_rows, _ = await service.find_all(
        FindAllReviews(search="", page=1, page_size=10)
    )
    assert repo.calls == []
    assert cached_rows[0].review_id == rows[0].review_id


async def test_query_empty_page_reports_zero_total() -> None:
    class EmptyRepo(FakeQueryRepo):
        async def find_all(self, request):
            return []

    rows, total = await _query_service(EmptyRepo(), FakeQueryCache()).find_all(
        FindAllReviews(search="", page=1, page_size=10)
    )
    assert rows == []
    assert total == 0


async def test_query_total_comes_from_window_count() -> None:
    class BigRepo(FakeQueryRepo):
        async def find_all(self, request):
            return [_list_row(1, total=42), _list_row(2, total=42)]

    rows, total = await _query_service(BigRepo(), FakeQueryCache()).find_all(
        FindAllReviews(search="", page=1, page_size=10)
    )
    assert len(rows) == 2
    assert total == 42


async def test_query_list_errors_substitute_service_sentinel() -> None:
    class FailingRepo(FakeQueryRepo):
        async def find_all(self, request):
            raise AppError("INTERNAL", 500, "failed to find all reviews")

    with pytest.raises(AppError) as excinfo:
        await _query_service(FailingRepo(), FakeQueryCache()).find_all(
            FindAllReviews(search="", page=1, page_size=10)
        )
    assert excinfo.value.is_(err_failed_find_all_reviews)


@pytest.mark.parametrize(
    ("method", "svc_request", "sentinel"),
    [
        (
            "find_by_product",
            FindAllReviewsByProduct(
                product_id=10, rating=0, search="", page=1, page_size=10
            ),
            err_failed_find_by_product_reviews,
        ),
        (
            "find_by_merchant",
            FindAllReviewsByMerchant(
                merchant_id=3, rating=0, search="", page=1, page_size=10
            ),
            err_failed_find_by_merchant_reviews,
        ),
        (
            "find_active",
            FindAllReviews(search="", page=1, page_size=10),
            err_failed_find_active_reviews,
        ),
        (
            "find_trashed",
            FindAllReviews(search="", page=1, page_size=10),
            err_failed_find_trashed_reviews,
        ),
    ],
)
async def test_query_each_list_substitutes_its_sentinel(
    method: str, svc_request: Any, sentinel: AppError
) -> None:
    class FailingRepo(FakeQueryRepo):
        pass

    async def boom(*_args, **_kwargs):
        raise AppError("INTERNAL", 500, "boom")

    setattr(FailingRepo, method, boom)
    with pytest.raises(AppError) as excinfo:
        await getattr(_query_service(FailingRepo(), FakeQueryCache()), method)(svc_request)
    assert excinfo.value.is_(sentinel)


async def test_query_find_by_id_cache_first_and_not_found() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    row = await service.find_by_id(7)
    assert row.review_id == 7
    assert cache.writes == ["id:7"]
    repo.calls.clear()

    cached = await service.find_by_id(7)
    assert repo.calls == []
    assert cached.review_id == 7

    class FailingRepo(FakeQueryRepo):
        async def find_by_id(self, review_id):
            raise AppError("INTERNAL", 500, "failed to find review by ID")

    with pytest.raises(AppError) as excinfo:
        await _query_service(FailingRepo(), FakeQueryCache()).find_by_id(9)
    assert excinfo.value.is_(err_review_not_found)


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


def _created_row(review_id: int = 9) -> ReviewRow:
    return ReviewRow(
        review_id=review_id,
        user_id=5,
        product_id=10,
        name="",
        comment="Produk bagus!",
        rating=5,
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request: CreateReviewRecord) -> ReviewRow:
        self.calls.append(
            f"create:{request.user_id}:{request.product_id}:{request.name}"
        )
        return _created_row()

    async def update(self, request: UpdateReviewRequest) -> ReviewRow:
        self.calls.append(f"update:{request.review_id}")
        return _created_row(review_id=request.review_id or 0)

    async def trash(self, review_id: int) -> Review:
        self.calls.append(f"trash:{review_id}")
        return Review(
            review_id=review_id,
            user_id=5,
            product_id=10,
            name="John",
            comment="c",
            rating=5,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=UPDATED,
        )

    async def restore(self, review_id: int) -> Review:
        self.calls.append(f"restore:{review_id}")
        return Review(
            review_id=review_id,
            user_id=5,
            product_id=10,
            name="John",
            comment="c",
            rating=5,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, review_id: int) -> bool:
        self.calls.append(f"delete:{review_id}")
        return True

    async def restore_all(self) -> bool:
        self.calls.append("restore_all")
        return True

    async def delete_all(self) -> bool:
        self.calls.append("delete_all")
        return True


class FakeCommandCache:
    def __init__(self) -> None:
        self.evicted: list[int] = []

    async def delete_cached_review(self, review_id: int) -> int:
        self.evicted.append(review_id)
        return 1


class FakeUserAdapter:
    def __init__(self, error: AppError | None = None) -> None:
        self.error = error
        self.calls: list[int] = []

    async def find_by_id(self, user_id: int) -> Any:
        self.calls.append(user_id)
        if self.error is not None:
            raise self.error
        return object()


class FakeProductAdapter:
    def __init__(self, error: AppError | None = None) -> None:
        self.error = error
        self.calls: list[int] = []

    async def find_by_id(self, product_id: int) -> Any:
        self.calls.append(product_id)
        if self.error is not None:
            raise self.error
        return _product_row()


def _command_service(
    repo: FakeCommandRepo,
    cache: FakeCommandCache,
    query_repo: Any = None,
    user: Any = None,
    product: Any = None,
) -> ReviewCommandServiceImpl:
    return ReviewCommandServiceImpl(
        repo,
        query_repo or FakeQueryRepo(),
        user or FakeUserAdapter(),
        product or FakeProductAdapter(),
        cache,
        _logger(),
        _obs(),
    )


async def test_command_create_validates_user_then_product_and_evicts() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    user, product = FakeUserAdapter(), FakeProductAdapter()
    service = _command_service(repo, cache, user=user, product=product)

    created = await service.create(
        CreateReviewRequest(user_id=5, product_id=10, rating=5, comment="Produk bagus!")
    )
    assert user.calls == [5]
    assert product.calls == [10]
    assert repo.calls == ["create:5:10:"]  # name is empty (request has none)
    assert created.review_id == 9
    assert cache.evicted == [9]


async def test_command_create_propagates_adapter_errors() -> None:
    service = _command_service(
        FakeCommandRepo(), FakeCommandCache(), user=FakeUserAdapter(err_user_not_found_repo)
    )
    with pytest.raises(AppError) as excinfo:
        await service.create(
            CreateReviewRequest(user_id=5, product_id=10, rating=5, comment="c")
        )
    assert excinfo.value is err_user_not_found_repo

    product = FakeProductAdapter(err_product_not_found)
    service = _command_service(
        FakeCommandRepo(), FakeCommandCache(), product=product
    )
    with pytest.raises(AppError) as excinfo:
        await service.create(
            CreateReviewRequest(user_id=5, product_id=10, rating=5, comment="c")
        )
    assert excinfo.value is err_product_not_found


async def test_command_create_repo_failure_substitutes_sentinel() -> None:
    class FailingRepo(FakeCommandRepo):
        async def create(self, request):
            raise AppError("INTERNAL", 500, "failed to create review")

    service = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.create(
            CreateReviewRequest(user_id=5, product_id=10, rating=5, comment="c")
        )
    assert excinfo.value.is_(err_failed_create_review)


async def test_command_update_precheck_and_evict() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    query_repo = FakeQueryRepo()
    service = _command_service(repo, cache, query_repo=query_repo)

    updated = await service.update(
        UpdateReviewRequest(review_id=7, name="", rating=4, comment="updated")
    )
    assert query_repo.calls == ["find_by_id:7"]
    assert repo.calls == ["update:7"]
    assert updated.review_id == 7
    assert cache.evicted == [7]


async def test_command_update_missing_review_maps_to_not_found() -> None:
    class MissingRepo(FakeQueryRepo):
        async def find_by_id(self, review_id):
            raise err_review_not_found

    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache, query_repo=MissingRepo())

    with pytest.raises(AppError) as excinfo:
        await service.update(
            UpdateReviewRequest(review_id=7, name="", rating=4, comment="c")
        )
    assert excinfo.value is err_review_not_found
    assert repo.calls == []
    assert cache.evicted == []


async def test_command_update_repo_failure_substitutes_sentinel() -> None:
    class FailingRepo(FakeCommandRepo):
        async def update(self, request):
            raise AppError("INTERNAL", 500, "failed to update review")

    service = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.update(
            UpdateReviewRequest(review_id=7, name="", rating=4, comment="c")
        )
    assert excinfo.value.is_(err_failed_update_review)


async def test_command_trash_restore_delete_evict() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    trashed = await service.trash(7)
    assert trashed.deleted_at is not None
    assert cache.evicted == [7]

    restored = await service.restore(7)
    assert restored.deleted_at is None
    assert cache.evicted == [7, 7]

    assert await service.delete_permanent(7) is True
    assert cache.evicted == [7, 7, 7]


async def test_command_trash_propagates_repo_error_unchanged() -> None:
    class FailingRepo(FakeCommandRepo):
        async def trash(self, review_id):
            raise err_review_not_found

    with pytest.raises(AppError) as excinfo:
        await _command_service(FailingRepo(), FakeCommandCache()).trash(2_000_000)
    assert excinfo.value is err_review_not_found


async def test_command_restore_all_substitutes_sentinel() -> None:
    class FailingRepo(FakeCommandRepo):
        async def restore_all(self):
            raise AppError("INTERNAL", 500, "failed to restore all reviews")

    with pytest.raises(AppError) as excinfo:
        await _command_service(FailingRepo(), FakeCommandCache()).restore_all()
    assert excinfo.value.is_(err_failed_restore_all_reviews)


async def test_command_delete_all_propagates_repo_error_unchanged() -> None:
    class FailingRepo(FakeCommandRepo):
        async def delete_all(self):
            raise AppError("INTERNAL", 500, "failed to permanently delete all reviews")

    with pytest.raises(AppError) as excinfo:
        await _command_service(FailingRepo(), FakeCommandCache()).delete_all()
    assert excinfo.value.message == "failed to permanently delete all reviews"


__all__ = []
