"""Review detail query service. Pagination is normalised once and the normalised values are used for both the cache key and the repository call. Reads are cache-first; a miss loads from the DB and populates the cache. Repository failures are propagated unchanged (the service forwards them through `errorhandler.HandleError`, which returns the `AppError`), so the wire code matches the repository error — a DB error during `find_all` surfaces as the repository's 404 `failed to find all review details`, not a 500."""

from __future__ import annotations

from pkg.database.schema.review_detail import (
    GetReviewDetailByIDRow,
    GetReviewDetailsActiveRow,
    GetReviewDetailsRow,
)
from pkg.logger.logger import Logger
from service.review_detail.redis.interfaces import ReviewDetailQueryCache
from service.review_detail.repository.interfaces import ReviewDetailQueryRepository
from shared.observability import Observability


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class ReviewDetailQueryServiceImpl:
    def __init__(
        self,
        repo: ReviewDetailQueryRepository,
        cache: ReviewDetailQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetReviewDetailsRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("review_detail.query.find_all", page=page, page_size=page_size):
            cached = await self._cache.get_review_details(page, page_size, search)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_all(search, page, page_size)
            except Exception as exc:
                self._logger.error("failed to fetch review details", error=str(exc))
                raise
            total = rows[0].total_count if rows else 0
            await self._cache.set_review_details(page, page_size, search, rows, total)
            return rows, total

    async def find_by_id(self, review_detail_id: int) -> GetReviewDetailByIDRow:
        with self._obs.span("review_detail.query.find_by_id", review_detail_id=review_detail_id):
            cached = await self._cache.get_review_detail_by_id(review_detail_id)
            if cached is not None:
                return cached
            review_detail = await self._repo.find_by_id(review_detail_id)
            await self._cache.set_review_detail_by_id(review_detail)
            return review_detail

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetReviewDetailsActiveRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("review_detail.query.find_active", page=page, page_size=page_size):
            cached = await self._cache.get_active(page, page_size, search)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_active(search, page, page_size)
            except Exception as exc:
                self._logger.error("failed to fetch active review details", error=str(exc))
                raise
            total = rows[0].total_count if rows else 0
            await self._cache.set_active(page, page_size, search, rows, total)
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetReviewDetailsActiveRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("review_detail.query.find_trashed", page=page, page_size=page_size):
            cached = await self._cache.get_trashed(page, page_size, search)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_trashed(search, page, page_size)
            except Exception as exc:
                self._logger.error("failed to fetch trashed review details", error=str(exc))
                raise
            total = rows[0].total_count if rows else 0
            await self._cache.set_trashed(page, page_size, search, rows, total)
            return rows, total


__all__ = ["ReviewDetailQueryServiceImpl", "normalize_pagination"]
