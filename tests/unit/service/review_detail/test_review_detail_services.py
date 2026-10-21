"""Unit tests for review detail query/command services and cache invalidation. Like the slider port, the query service caches `find_all`/`find_active`/ `find_trashed`/`find_by_id` and serves them cache-first. The command service invalidates the entire `review_detail:*` cache on *every single* mutation — but, unlike the slider port, it deliberately does **not** flush the cache on the bulk `restore_all`/`delete_all` operations, matching the review_detail service (see). `delete_permanent` first resolves the trashed row via the read repository (which raises 404 `review detail not found` if absent), then removes the backing file, then hard-deletes."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from pkg.database.schema.review_detail import (
    CreateReviewDetailRow,
    GetReviewDetailByIDRow,
    GetReviewDetailsActiveRow,
    GetReviewDetailsRow,
    ReviewDetail,
)
from pkg.logger.logger import Logger
from service.review_detail.service.review_detail_command_service import (
    ReviewDetailCommandServiceImpl,
)
from service.review_detail.service.review_detail_query_service import (
    ReviewDetailQueryServiceImpl,
    normalize_pagination,
)
from shared.domain.requests.review_detail import (
    CreateReviewDetailRequest,
    UpdateReviewDetailRequest,
)
from shared.errors import AppError
from shared.observability import Observability

CREATED = datetime(2026, 1, 2)
UPDATED = datetime(2026, 1, 3)
DELETED = datetime(2026, 2, 1)


def _row(review_detail_id: int = 1, total: int = 1) -> GetReviewDetailsRow:
    return GetReviewDetailsRow(
        review_detail_id=review_detail_id,
        review_id=10,
        type="photo",
        url="/img/a.png",
        caption="Nice",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(review_detail_id: int = 1, total: int = 1) -> GetReviewDetailsActiveRow:
    return GetReviewDetailsActiveRow(
        review_detail_id=review_detail_id,
        review_id=11,
        type="video",
        url="/img/b.png",
        caption="Bad",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=total,
    )


def _by_id_row(review_detail_id: int = 1) -> GetReviewDetailByIDRow:
    return GetReviewDetailByIDRow(
        review_detail_id=review_detail_id,
        review_id=12,
        type="photo",
        url="/img/a.png",
        caption="cap",
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

    async def find_by_id(self, review_detail_id):
        self.calls.append(f"find_by_id:{review_detail_id}")
        return _by_id_row(review_detail_id)

    async def find_by_id_trashed(self, review_detail_id):
        self.calls.append(f"find_by_id_trashed:{review_detail_id}")
        return ReviewDetail(
            review_detail_id=review_detail_id,
            review_id=12,
            type="photo",
            url="/img/a.png",
            caption="cap",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_review_details(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_review_details(self, page, page_size, search, rows, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (rows, total)

    async def get_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_active(self, page, page_size, search, rows, total):
        self.store[f"active:{page}:{page_size}:{search}"] = (rows, total)

    async def get_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_trashed(self, page, page_size, search, rows, total):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (rows, total)

    async def get_review_detail_by_id(self, review_detail_id):
        return self.store.get(f"id:{review_detail_id}")

    async def set_review_detail_by_id(self, row):
        if row is None:
            return
        self.writes.append(f"id:{row.review_detail_id}")
        self.store[f"id:{row.review_detail_id}"] = row


def _logger() -> Logger:
    return Logger("test", "error")


def _query_service(repo: FakeQueryRepo, cache: FakeQueryCache) -> ReviewDetailQueryServiceImpl:
    logger = _logger()
    return ReviewDetailQueryServiceImpl(repo, cache, logger, Observability("test", logger))


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
    cache.store["active:1:10:"] = ([_active_row(review_detail_id=1)], 1)
    cache.store["trashed:1:10:"] = ([_active_row(review_detail_id=2)], 1)

    active_rows, _ = await service.find_active("", 1, 10)
    trashed_rows, _ = await service.find_trashed("", 1, 10)

    assert repo.calls == []
    assert active_rows[0].review_detail_id == 1
    assert trashed_rows[0].review_detail_id == 2


async def test_find_by_id_caches_and_is_cache_first() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    row = await service.find_by_id(10)
    assert repo.calls == ["find_by_id:10"]
    assert cache.writes == ["id:10"]
    repo.calls.clear()

    cached = await service.find_by_id(10)
    assert repo.calls == []
    assert cached.review_detail_id == row.review_detail_id


async def test_query_failure_propagates_repo_error() -> None:
    class FailingRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            raise AppError("NOT_FOUND", 404, "failed to find all review details")

    service = _query_service(FailingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as excinfo:
        await service.find_all("", 1, 10)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "failed to find all review details"


async def test_find_by_id_propagates_not_found() -> None:
    class MissingRepo(FakeQueryRepo):
        async def find_by_id(self, review_detail_id):
            raise AppError("NOT_FOUND", 404, "review detail not found")

    service = _query_service(MissingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as excinfo:
        await service.find_by_id(999)
    assert excinfo.value.code == 404


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request):
        self.calls.append(f"create:{request.review_id}")
        return CreateReviewDetailRow(
            review_detail_id=9,
            review_id=request.review_id,
            type=request.type,
            url=request.url,
            caption=request.caption,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.review_detail_id}")
        return GetReviewDetailByIDRow(
            review_detail_id=request.review_detail_id or 1,
            review_id=12,
            type=request.type,
            url=request.url,
            caption=request.caption,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, review_detail_id):
        self.calls.append(f"trash:{review_detail_id}")
        return ReviewDetail(
            review_detail_id=review_detail_id,
            review_id=12,
            type="photo",
            url="/img/a.png",
            caption="cap",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, review_detail_id):
        self.calls.append(f"restore:{review_detail_id}")
        return ReviewDetail(
            review_detail_id=review_detail_id,
            review_id=12,
            type="photo",
            url="/img/a.png",
            caption="cap",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, review_detail_id):
        self.calls.append(f"delete:{review_detail_id}")
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

    async def invalidate_review_detail_cache(self) -> int:
        self.invalidations += 1
        return 1

    async def delete_review_detail_cache(self, review_detail_id: int) -> int:
        self.invalidations += 1
        return 1


def _command_service(
    repo: FakeCommandRepo,
    cache: FakeCommandCache,
    query_repo: FakeQueryRepo | None = None,
) -> ReviewDetailCommandServiceImpl:
    logger = _logger()
    return ReviewDetailCommandServiceImpl(
        repo, query_repo or FakeQueryRepo(), cache, logger, Observability("test", logger)
    )


async def test_create_invalidates_cache() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    row = await service.create(
        CreateReviewDetailRequest(review_id=5, type="photo", url="/img/a.png", caption="cap")
    )

    assert row.review_detail_id == 9
    assert cache.invalidations == 1


async def test_update_invalidates_cache() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.update(
        UpdateReviewDetailRequest(
            review_detail_id=4, type="photo", url="/a.png", caption="cap"
        )
    )

    assert cache.invalidations == 1


async def test_trash_restore_delete_invalidate() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)

    assert cache.invalidations == 3


async def test_restore_all_and_delete_all_do_not_invalidate() -> None:
    """review_detail service does NOT flush the cache on bulk ops."""
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.restore_all()
    await service.delete_all_permanent()

    assert cache.invalidations == 0


async def test_trash_propagates_not_found() -> None:
    class MissingRepo(FakeCommandRepo):
        async def trash(self, review_detail_id):
            raise AppError("NOT_FOUND", 404, "review detail not found")

    service = _command_service(MissingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.trash(7)
    assert excinfo.value.code == 404


async def test_delete_permanent_resolves_trashed_row_then_deletes() -> None:
    repo, cache, query_repo = FakeCommandRepo(), FakeCommandCache(), FakeQueryRepo()
    service = _command_service(repo, cache, query_repo)

    result = await service.delete_permanent(7)

    assert result is True
    assert "find_by_id_trashed:7" in query_repo.calls
    assert "delete:7" in repo.calls


async def test_delete_permanent_propagates_not_found() -> None:
    class MissingQueryRepo(FakeQueryRepo):
        async def find_by_id_trashed(self, review_detail_id):
            raise AppError("NOT_FOUND", 404, "review detail not found")

    repo = FakeCommandRepo()
    cache = FakeCommandCache()
    logger = _logger()
    service = ReviewDetailCommandServiceImpl(
        repo, MissingQueryRepo(), cache, logger, Observability("test", logger)
    )
    with pytest.raises(AppError) as excinfo:
        await service.delete_permanent(7)
    assert excinfo.value.code == 404


async def test_create_failure_propagates_repo_error() -> None:
    class FailingRepo(FakeCommandRepo):
        async def create(self, request):
            raise AppError("INTERNAL", 500, "failed to create review detail")

    cache = FakeCommandCache()
    service = _command_service(FailingRepo(), cache)
    with pytest.raises(AppError) as excinfo:
        await service.create(
            CreateReviewDetailRequest(
                review_id=5, type="photo", url="/img/a.png", caption="cap"
            )
        )
    assert excinfo.value.code == 500
    # No invalidation when the repository failed before commit.
    assert cache.invalidations == 0


__all__ = []
