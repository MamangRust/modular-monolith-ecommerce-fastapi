"""Unit tests for banner query/command services and cache invalidation."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from pkg.database.schema.banner import (
    Banner,
    CreateBannerRow,
    GetBannerRow,
    GetBannersActiveRow,
    GetBannersRow,
    UpdateBannerRow,
)
from pkg.logger.logger import Logger
from service.banner.service.banner_command_service import BannerCommandServiceImpl
from service.banner.service.banner_query_service import (
    BannerQueryServiceImpl,
    normalize_pagination,
)
from shared.domain.requests.banner import CreateBannerRequest, UpdateBannerRequest
from shared.observability import Observability

CREATED = datetime(2026, 1, 1, 10, 0, 0)
UPDATED = datetime(2026, 1, 2, 10, 0, 0)


def _row(banner_id: int = 1, total: int = 1) -> GetBannersRow:
    return GetBannersRow(
        banner_id=banner_id,
        name="Banner 1",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31),
        start_time=time(8, 0),
        end_time=time(16, 0),
        is_active=True,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(banner_id: int = 1, total: int = 1) -> GetBannersActiveRow:
    return GetBannersActiveRow(
        banner_id=banner_id,
        name="Banner 1",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31),
        start_time=time(8, 0),
        end_time=time(16, 0),
        is_active=True,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=total,
    )


def _by_id(banner_id: int = 1) -> GetBannerRow:
    return GetBannerRow(
        banner_id=banner_id,
        name="Banner 1",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31),
        start_time=time(8, 0),
        end_time=time(16, 0),
        is_active=True,
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_all(self, search, page, page_size):
        self.calls.append(f"find_all:{search}:{page}:{page_size}")
        return [_row(total=1)]

    async def find_by_id(self, banner_id):
        self.calls.append(f"find_by_id:{banner_id}")
        return _by_id(banner_id)

    async def find_active(self, search, page, page_size):
        self.calls.append(f"find_active:{search}:{page}:{page_size}")
        return [_active_row(total=1)]

    async def find_trashed(self, search, page, page_size):
        self.calls.append(f"find_trashed:{search}:{page}:{page_size}")
        return [_active_row(total=1)]


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_banners(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_banners(self, page, page_size, search, banners, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (banners, total)

    async def get_banner_by_id(self, banner_id):
        return self.store.get(f"id:{banner_id}")

    async def set_banner_by_id(self, banner):
        self.writes.append(f"id:{banner.banner_id}")
        self.store[f"id:{banner.banner_id}"] = banner

    async def get_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_active(self, page, page_size, search, banners, total):
        self.store[f"active:{page}:{page_size}:{search}"] = (banners, total)

    async def get_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_trashed(self, page, page_size, search, banners, total):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (banners, total)


def _query_service(
    repo: FakeQueryRepo, cache: FakeQueryCache
) -> BannerQueryServiceImpl:
    logger = Logger("test", "error")
    return BannerQueryServiceImpl(repo, cache, logger, Observability("test", logger))


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
    banner = await service.find_by_id(5)
    assert banner.banner_id == 5
    assert "id:5" in cache.writes
    repo.calls.clear()
    await service.find_by_id(5)
    assert repo.calls == []


async def test_find_active_and_trashed_cache() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)
    cache.store["active:1:10:"] = ([_active_row()], 1)
    cache.store["trashed:1:10:"] = ([_active_row(banner_id=2)], 1)

    active_rows, _ = await service.find_active("", 1, 10)
    trashed_rows, _ = await service.find_trashed("", 1, 10)

    assert repo.calls == []
    assert active_rows[0].banner_id == 1
    assert trashed_rows[0].banner_id == 2


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request):
        self.calls.append(f"create:{request.name}")
        return CreateBannerRow(
            banner_id=9,
            name=request.name,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
            start_time=time(8, 0),
            end_time=time(16, 0),
            is_active=request.is_active,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.banner_id}:{request.name}")
        return UpdateBannerRow(
            banner_id=request.banner_id or 0,
            name=request.name,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
            start_time=time(8, 0),
            end_time=time(16, 0),
            is_active=request.is_active,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, banner_id):
        self.calls.append(f"trash:{banner_id}")
        return Banner(
            banner_id=banner_id,
            name="B",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
            start_time=time(8, 0),
            end_time=time(16, 0),
            is_active=True,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=UPDATED,
        )

    async def restore(self, banner_id):
        self.calls.append(f"restore:{banner_id}")
        return Banner(
            banner_id=banner_id,
            name="B",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
            start_time=time(8, 0),
            end_time=time(16, 0),
            is_active=True,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, banner_id):
        self.calls.append(f"delete:{banner_id}")

    async def restore_all(self):
        self.calls.append("restore_all")

    async def delete_all_permanent(self):
        self.calls.append("delete_all")


class FakeCommandCache:
    def __init__(self) -> None:
        self.invalidated: list[int] = []
        self.list_invalidations = 0
        self.all_invalidations = 0

    async def delete_cached_banner(self, banner_id):
        self.invalidated.append(banner_id)
        return 1

    async def invalidate_lists(self):
        self.list_invalidations += 1
        return 1

    async def invalidate_banner(self, banner_id):
        self.invalidated.append(banner_id)
        return 1

    async def invalidate_all(self):
        self.all_invalidations += 1
        return 1


def _command_service(
    repo: FakeCommandRepo, cache: FakeCommandCache
) -> BannerCommandServiceImpl:
    logger = Logger("test", "error")
    return BannerCommandServiceImpl(repo, cache, logger, Observability("test", logger))


def _create_request(name: str = "New") -> CreateBannerRequest:
    return CreateBannerRequest(
        name=name,
        start_date="2023-01-01",
        end_date="2023-01-31",
        start_time="08:00:00",
        end_time="16:00:00",
        is_active=True,
    )


def _update_request(banner_id: int = 4) -> UpdateBannerRequest:
    return UpdateBannerRequest(
        banner_id=banner_id,
        name="Renamed",
        start_date="2023-01-01",
        end_date="2023-01-31",
        start_time="08:00:00",
        end_time="16:00:00",
        is_active=False,
    )


async def test_create_invalidates_lists_after_commit() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)
    banner = await service.create(_create_request())
    assert banner.banner_id == 9
    assert cache.list_invalidations == 1


async def test_update_invalidates_by_id_and_lists() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)
    await service.update(_update_request(4))
    assert cache.invalidated == [4]


async def test_trash_restore_delete_invalidate() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)
    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)
    assert cache.invalidated == [2, 2, 2]


async def test_bulk_commands_invalidate_everything() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)
    await service.restore_all()
    await service.delete_all_permanent()
    assert cache.all_invalidations == 2
