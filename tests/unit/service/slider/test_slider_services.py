"""Unit tests for slider query/command services and cache invalidation. The slider query service **propagates** repository failures unchanged (the service forwards them through `errorhandler.HandleError`, which returns the `AppError`), so a DB error during `find_all` surfaces as the repository's 404 `failed to find all sliders`. The command service invalidates the entire `slider:*` cache on *every* mutation — including `restore_all`/ `delete_all`, which slider service DOES flush (unlike shipping_address)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from pkg.database.schema.slider import (
    CreateSliderRow,
    GetSliderByIDRow,
    GetSlidersActiveRow,
    GetSlidersRow,
    Slider,
)
from pkg.logger.logger import Logger
from service.slider.service.slider_command_service import SliderCommandServiceImpl
from service.slider.service.slider_query_service import (
    SliderQueryServiceImpl,
    normalize_pagination,
)
from shared.domain.requests.slider import CreateSliderRequest, UpdateSliderRequest
from shared.errors import AppError
from shared.observability import Observability

CREATED = datetime(2026, 1, 2)
UPDATED = datetime(2026, 1, 3)
DELETED = datetime(2026, 2, 1)


def _row(slider_id: int = 1, total: int = 1) -> GetSlidersRow:
    return GetSlidersRow(
        slider_id=slider_id,
        name="Hero",
        image="/img/a.png",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(slider_id: int = 1, total: int = 1) -> GetSlidersActiveRow:
    return GetSlidersActiveRow(
        slider_id=slider_id,
        name="Hero",
        image="/img/a.png",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=total,
    )


def _by_id_row(slider_id: int = 1) -> GetSliderByIDRow:
    return GetSliderByIDRow(
        slider_id=slider_id,
        name="Hero",
        image="/img/a.png",
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_all(self, search, page, page_size):
        self.calls.append(f"find_all:{search}:{page}:{page_size}")
        return [_row(total=1)]

    async def find_active(self, search, page, page_size):
        self.calls.append(f"find_active:{search}:{page}:{page_size}")
        return [_active_row(total=1)]

    async def find_trashed(self, search, page, page_size):
        self.calls.append(f"find_trashed:{search}:{page}:{page_size}")
        return [_active_row(total=1)]

    async def find_by_id(self, slider_id):
        self.calls.append(f"find_by_id:{slider_id}")
        return _by_id_row(slider_id)


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_sliders(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_sliders(self, page, page_size, search, rows, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (rows, total)

    async def get_slider_by_id(self, slider_id):
        return self.store.get(f"id:{slider_id}")

    async def set_slider_by_id(self, row):
        if row is None:
            return
        self.writes.append(f"id:{row.slider_id}")
        self.store[f"id:{row.slider_id}"] = row

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


def _query_service(repo: FakeQueryRepo, cache: FakeQueryCache) -> SliderQueryServiceImpl:
    logger = _logger()
    return SliderQueryServiceImpl(repo, cache, logger, Observability("test", logger))


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

    _, total = await service.find_all("", 1, 10)

    assert repo.calls == []
    assert total == 1


async def test_find_active_and_trashed_cache() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)
    cache.store["active:1:10:"] = ([_active_row(slider_id=1)], 1)
    cache.store["trashed:1:10:"] = ([_active_row(slider_id=2)], 1)

    active_rows, _ = await service.find_active("", 1, 10)
    trashed_rows, _ = await service.find_trashed("", 1, 10)

    assert repo.calls == []
    assert active_rows[0].slider_id == 1
    assert trashed_rows[0].slider_id == 2


async def test_find_by_id_caches_and_is_cache_first() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    row = await service.find_by_id(10)
    assert repo.calls == ["find_by_id:10"]
    assert cache.writes == ["id:10"]
    repo.calls.clear()

    cached = await service.find_by_id(10)
    assert repo.calls == []
    assert cached.slider_id == row.slider_id


async def test_query_failure_propagates_repo_error() -> None:
    class FailingRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            raise AppError("NOT_FOUND", 404, "failed to find all sliders")

    service = _query_service(FailingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as excinfo:
        await service.find_all("", 1, 10)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "failed to find all sliders"


async def test_find_by_id_propagates_not_found() -> None:
    class MissingRepo(FakeQueryRepo):
        async def find_by_id(self, slider_id):
            raise AppError("NOT_FOUND", 404, "failed to find slider by ID")

    service = _query_service(MissingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as excinfo:
        await service.find_by_id(999)
    assert excinfo.value.code == 404


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request):
        self.calls.append(f"create:{request.name}")
        return CreateSliderRow(
            slider_id=9,
            name=request.name,
            image=request.image,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.slider_id}")
        return CreateSliderRow(
            slider_id=request.slider_id or 1,
            name=request.name,
            image=request.image,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, slider_id):
        self.calls.append(f"trash:{slider_id}")
        return Slider(
            slider_id=slider_id,
            name="Hero",
            image="/img/a.png",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, slider_id):
        self.calls.append(f"restore:{slider_id}")
        return Slider(
            slider_id=slider_id,
            name="Hero",
            image="/img/a.png",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, slider_id):
        self.calls.append(f"delete:{slider_id}")
        return True

    async def restore_all(self):
        self.calls.append("restore_all")
        return True

    async def delete_all_permanent(self):
        self.calls.append("delete_all")
        return True


class FakeCommandCache:
    def __init__(self) -> None:
        self.invalidations = 0

    async def delete_slider_cache(self, slider_id: int) -> int:
        self.invalidations += 1
        return 1

    async def invalidate_slider_cache(self) -> int:
        self.invalidations += 1
        return 1


def _command_service(
    repo: FakeCommandRepo, cache: FakeCommandCache
) -> SliderCommandServiceImpl:
    logger = _logger()
    return SliderCommandServiceImpl(repo, cache, logger, Observability("test", logger))


async def test_create_invalidates_cache() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    row = await service.create(CreateSliderRequest(name="Hero", image="/img/a.png"))

    assert row.slider_id == 9
    assert cache.invalidations == 1


async def test_update_invalidates_cache() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.update(UpdateSliderRequest(slider_id=4, name="Hero", image="/a.png"))

    assert cache.invalidations == 1


async def test_trash_restore_delete_invalidate() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)

    assert cache.invalidations == 3


async def test_restore_all_and_delete_all_invalidate() -> None:
    """slider service DOES flush the cache on bulk ops."""
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.restore_all()
    await service.delete_all_permanent()

    assert cache.invalidations == 2


async def test_trash_propagates_not_found() -> None:
    class MissingRepo(FakeCommandRepo):
        async def trash(self, slider_id):
            raise AppError("NOT_FOUND", 404, "slider not found")

    service = _command_service(MissingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.trash(7)
    assert excinfo.value.code == 404


async def test_delete_permanent_propagates_repository_error() -> None:
    class MissingRepo(FakeCommandRepo):
        async def delete_permanent(self, slider_id):
            raise AppError("NOT_FOUND", 404, "slider not found")

    service = _command_service(MissingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.delete_permanent(7)
    assert excinfo.value.code == 404


async def test_create_failure_propagates_repo_error() -> None:
    class FailingRepo(FakeCommandRepo):
        async def create(self, request):
            raise AppError("INTERNAL", 500, "failed to create slider")

    cache = FakeCommandCache()
    service = _command_service(FailingRepo(), cache)
    with pytest.raises(AppError) as excinfo:
        await service.create(CreateSliderRequest(name="Hero", image="/a.png"))
    assert excinfo.value.code == 500
    # No invalidation when the repository failed before commit.
    assert cache.invalidations == 0


async def test_restore_all_failure_propagates_repo_error() -> None:
    class FailingRepo(FakeCommandRepo):
        async def restore_all(self):
            raise AppError("INTERNAL", 500, "failed to restore all sliders")

    service = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.restore_all()
    assert excinfo.value.code == 500


__all__ = []
