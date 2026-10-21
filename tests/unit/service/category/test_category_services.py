"""Unit tests for category query/command/stats services and cache invalidation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from pkg.database.schema.category import (
    Category,
    CreateCategoryRow,
    GetCategoriesActiveRow,
    GetCategoriesRow,
    GetCategoryByIDRow,
    GetMonthlyCategoryRow,
    GetMonthlyTotalPriceRow,
    GetYearlyCategoryRow,
    GetYearlyTotalPriceRow,
)
from pkg.logger.logger import Logger
from pkg.utils.slug import make_slug
from service.category.service.category_command_service import (
    CategoryCommandServiceImpl,
)
from service.category.service.category_query_service import (
    CategoryQueryServiceImpl,
    normalize_pagination,
)
from service.category.service.category_stats_service import CategoryStatsServiceImpl
from shared.domain.requests.category import (
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from shared.errors import AppError
from shared.observability import Observability

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)


def _row(category_id: int = 1, total: int = 1) -> GetCategoriesRow:
    return GetCategoriesRow(
        category_id=category_id,
        name="Elektronik",
        description="desc",
        slug_category="elektronik",
        image_category="elektronik.png",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(category_id: int = 1, total: int = 1) -> GetCategoriesActiveRow:
    return GetCategoriesActiveRow(
        category_id=category_id,
        name="Elektronik",
        description="desc",
        slug_category="elektronik",
        image_category="elektronik.png",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=total,
    )


def _by_id(category_id: int = 1) -> GetCategoryByIDRow:
    return GetCategoryByIDRow(
        category_id=category_id,
        name="Elektronik",
        description="desc",
        slug_category="elektronik",
        image_category="elektronik.png",
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_all(self, search, page, page_size):
        self.calls.append(f"find_all:{search}:{page}:{page_size}")
        return [_row(total=1)]

    async def find_by_id(self, category_id):
        self.calls.append(f"find_by_id:{category_id}")
        return _by_id(category_id)

    async def find_active(self, search, page, page_size):
        self.calls.append(f"find_active:{search}:{page}:{page_size}")
        return [_active_row(total=1)]

    async def find_trashed(self, search, page, page_size):
        self.calls.append(f"find_trashed:{search}:{page}:{page_size}")
        return [_active_row(total=1)]

    async def find_by_id_trashed(self, category_id):
        self.calls.append(f"find_by_id_trashed:{category_id}")
        return Category(
            category_id=category_id,
            name="Elektronik",
            description="desc",
            slug_category="elektronik",
            image_category="elektronik.png",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=UPDATED,
        )


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_categories(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_categories(self, page, page_size, search, rows, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (rows, total)

    async def get_category_by_id(self, category_id):
        return self.store.get(f"id:{category_id}")

    async def set_category_by_id(self, category):
        self.writes.append(f"id:{category.category_id}")
        self.store[f"id:{category.category_id}"] = category

    async def get_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_active(self, page, page_size, search, rows, total):
        self.store[f"active:{page}:{page_size}:{search}"] = (rows, total)

    async def get_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_trashed(self, page, page_size, search, rows, total):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (rows, total)


def _logger() -> Logger:
    return Logger("test", "error")


def _query_service(
    repo: FakeQueryRepo, cache: FakeQueryCache
) -> CategoryQueryServiceImpl:
    logger = _logger()
    return CategoryQueryServiceImpl(repo, cache, logger, Observability("test", logger))


async def test_normalize_pagination() -> None:
    assert normalize_pagination(0, 0) == (1, 10)
    assert normalize_pagination(-3, -1) == (1, 10)
    assert normalize_pagination(2, 25) == (2, 25)


async def test_find_all_normalizes_and_caches() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    rows, total = await service.find_all("", 0, 0)

    assert repo.calls == ["find_all::1:10"]
    assert cache.writes == ["all:1:10:"]
    assert total == 1
    assert rows[0].total_count == 1


async def test_find_all_served_from_cache() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)
    await service.find_all("", 1, 10)
    repo.calls.clear()

    rows, total = await service.find_all("", 1, 10)

    assert repo.calls == []
    assert total == 1


async def test_find_by_id_caches_result() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)
    category = await service.find_by_id(5)
    assert category.category_id == 5
    assert "id:5" in cache.writes
    repo.calls.clear()
    await service.find_by_id(5)
    assert repo.calls == []


async def test_find_active_and_trashed_cache() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)
    cache.store["active:1:10:"] = ([_active_row()], 1)
    cache.store["trashed:1:10:"] = ([_active_row(category_id=2)], 1)

    active_rows, _ = await service.find_active("", 1, 10)
    trashed_rows, _ = await service.find_trashed("", 1, 10)

    assert repo.calls == []
    assert active_rows[0].category_id == 1
    assert trashed_rows[0].category_id == 2


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.last_slug: str | None = None

    async def create(self, request):
        self.calls.append(f"create:{request.name}")
        self.last_slug = request.slug_category
        return CreateCategoryRow(
            category_id=9,
            name=request.name,
            description=request.description,
            slug_category=request.slug_category,
            image_category=request.image_category,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.category_id}:{request.name}")
        self.last_slug = request.slug_category
        return _by_id(request.category_id or 0)

    async def trash(self, category_id):
        self.calls.append(f"trash:{category_id}")
        return Category(
            category_id=category_id,
            name="Elektronik",
            description="desc",
            slug_category="elektronik",
            image_category="elektronik.png",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=UPDATED,
        )

    async def restore(self, category_id):
        self.calls.append(f"restore:{category_id}")
        return Category(
            category_id=category_id,
            name="Elektronik",
            description="desc",
            slug_category="elektronik",
            image_category="elektronik.png",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, category_id):
        self.calls.append(f"delete:{category_id}")
        return True

    async def restore_all(self):
        self.calls.append("restore_all")
        return True

    async def delete_all(self):
        self.calls.append("delete_all")
        return True


class FakeCommandCache:
    def __init__(self) -> None:
        self.invalidated: list[int] = []
        self.list_invalidations = 0
        self.all_invalidations = 0

    async def delete_cached_category(self, category_id):
        self.invalidated.append(category_id)
        return 1

    async def invalidate_lists(self):
        self.list_invalidations += 1
        return 1

    async def invalidate_category(self, category_id):
        self.invalidated.append(category_id)
        return 1

    async def invalidate_all(self):
        self.all_invalidations += 1
        return 1


def _command_service(
    repo: FakeCommandRepo, query_repo: FakeQueryRepo, cache: FakeCommandCache
) -> CategoryCommandServiceImpl:
    logger = _logger()
    return CategoryCommandServiceImpl(
        repo, query_repo, cache, logger, Observability("test", logger)
    )


def _create_request(slug: str = "") -> CreateCategoryRequest:
    return CreateCategoryRequest(
        name="Elektronik",
        description="desc",
        slug_category=slug,
        image_category="elektronik.png",
    )


def _update_request(category_id: int = 4, slug: str = "") -> UpdateCategoryRequest:
    return UpdateCategoryRequest(
        category_id=category_id,
        name="Renamed",
        description="desc",
        slug_category=slug,
        image_category="renamed.png",
    )


async def test_create_generates_slug_when_missing_and_invalidates_lists() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, FakeQueryRepo(), cache)

    category = await service.create(_create_request())

    assert category.category_id == 9
    assert repo.last_slug is not None
    assert repo.last_slug.startswith(make_slug("Elektronik"))
    assert cache.list_invalidations == 1


async def test_create_keeps_provided_slug() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, FakeQueryRepo(), cache)

    await service.create(_create_request(slug="custom-slug"))

    assert repo.last_slug == "custom-slug"


async def test_update_generates_slug_and_invalidates_by_id() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, FakeQueryRepo(), cache)

    await service.update(_update_request(4))

    assert repo.last_slug is not None
    assert repo.last_slug.startswith(make_slug("Renamed"))
    assert cache.invalidated == [4]


async def test_trash_restore_delete_invalidate() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, FakeQueryRepo(), cache)

    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)

    assert cache.invalidated == [2, 2, 2]


async def test_delete_permanent_requires_trashed_row() -> None:
    repo, query_repo, cache = FakeCommandRepo(), FakeQueryRepo(), FakeCommandCache()
    service = _command_service(repo, query_repo, cache)

    await service.delete_permanent(7)

    assert "find_by_id_trashed:7" in query_repo.calls
    assert "delete:7" in repo.calls


async def test_delete_permanent_missing_row_raises() -> None:
    class MissingQueryRepo(FakeQueryRepo):
        async def find_by_id_trashed(self, category_id):
            raise AppError("NOT_FOUND", 404, "Category not found")

    service = _command_service(FakeCommandRepo(), MissingQueryRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.delete_permanent(7)
    assert excinfo.value.code == 404


def _trashed_with_image(category_id: int, image: str | None) -> Category:
    return Category(
        category_id=category_id,
        name="Elektronik",
        description="desc",
        slug_category="elektronik",
        image_category=image,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=UPDATED,
    )


async def test_delete_permanent_removes_image_file(tmp_path) -> None:
    image = tmp_path / "cat.png"
    image.write_bytes(b"img")

    class ImageQueryRepo(FakeQueryRepo):
        async def find_by_id_trashed(self, category_id):
            return _trashed_with_image(category_id, str(image))

    service = _command_service(FakeCommandRepo(), ImageQueryRepo(), FakeCommandCache())
    await service.delete_permanent(9)

    assert not image.exists()


async def test_delete_permanent_ignores_missing_image_file(tmp_path) -> None:
    missing = tmp_path / "gone.png"

    class ImageQueryRepo(FakeQueryRepo):
        async def find_by_id_trashed(self, category_id):
            return _trashed_with_image(category_id, str(missing))

    service = _command_service(FakeCommandRepo(), ImageQueryRepo(), FakeCommandCache())
    # FileNotFoundError (os.IsNotExist) is swallowed.
    await service.delete_permanent(9)


async def test_delete_permanent_remove_failure_raises(monkeypatch) -> None:
    class ImageQueryRepo(FakeQueryRepo):
        async def find_by_id_trashed(self, category_id):
            return _trashed_with_image(category_id, "uploads/category/x.png")

    def boom(path: str) -> None:
        raise PermissionError("nope")

    monkeypatch.setattr(
        "service.category.service.category_command_service.os.remove", boom
    )
    service = _command_service(FakeCommandRepo(), ImageQueryRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.delete_permanent(9)
    assert excinfo.value.message == "Failed to remove image category"


async def test_bulk_commands_invalidate_everything() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, FakeQueryRepo(), cache)

    await service.restore_all()
    await service.delete_all()

    assert cache.all_invalidations == 2


class FakeStatsRepo:
    def __init__(self) -> None:
        self.calls = 0

    async def get_monthly_total_price(self, year, month):
        self.calls += 1
        return [GetMonthlyTotalPriceRow(year="2026", month="01", total_revenue=1)]

    async def get_yearly_total_prices(self, year):
        self.calls += 1
        return [GetYearlyTotalPriceRow(year="2026", total_revenue=1)]

    async def get_month_price(self, year):
        self.calls += 1
        return [
            GetMonthlyCategoryRow(
                month="01",
                category_id=1,
                category_name="E",
                order_count=1,
                items_sold=1,
                total_revenue=1,
            )
        ]

    async def get_year_price(self, year):
        self.calls += 1
        return [
            GetYearlyCategoryRow(
                year="2026",
                category_id=1,
                category_name="E",
                order_count=1,
                items_sold=1,
                total_revenue=1,
                unique_products_sold=1,
            )
        ]


class FakeStatsCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}

    async def get_month_total_price(self, year, month):
        return self.store.get(f"mt:{year}:{month}")

    async def set_month_total_price(self, year, month, rows):
        self.store[f"mt:{year}:{month}"] = rows

    async def get_year_total_price(self, year):
        return self.store.get(f"yt:{year}")

    async def set_year_total_price(self, year, rows):
        self.store[f"yt:{year}"] = rows

    async def get_month_price(self, year):
        return self.store.get(f"mp:{year}")

    async def set_month_price(self, year, rows):
        self.store[f"mp:{year}"] = rows

    async def get_year_price(self, year):
        return self.store.get(f"yp:{year}")

    async def set_year_price(self, year, rows):
        self.store[f"yp:{year}"] = rows


def _stats_service(
    repo: FakeStatsRepo, cache: FakeStatsCache
) -> CategoryStatsServiceImpl:
    logger = _logger()
    return CategoryStatsServiceImpl(repo, cache, logger, Observability("test", logger))


async def test_stats_service_is_cache_first() -> None:
    repo, cache = FakeStatsRepo(), FakeStatsCache()
    service = _stats_service(repo, cache)

    first = await service.find_monthly_total_price(2026, 1)
    second = await service.find_monthly_total_price(2026, 1)

    assert repo.calls == 1
    assert first == second
    assert cache.store["mt:2026:1"] == first


async def test_stats_service_year_price_key_is_distinct_from_year_total() -> None:
    """split colliding `year` cache key."""
    repo, cache = FakeStatsRepo(), FakeStatsCache()
    service = _stats_service(repo, cache)

    await service.find_yearly_total_price(2026)
    await service.find_year_price(2026)

    assert "yt:2026" in cache.store
    assert "yp:2026" in cache.store
    assert repo.calls == 2
