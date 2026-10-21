"""Category query service.

Pagination is normalised once and the normalised values are used for both
the cache key and the repository call. Reads are cache-first; a miss loads
from the DB and populates the cache."""

from __future__ import annotations

from pkg.database.schema.category import (
    GetCategoriesActiveRow,
    GetCategoriesRow,
    GetCategoryByIDRow,
)
from pkg.logger.logger import Logger
from service.category.redis.interfaces import CategoryQueryCache
from service.category.repository.interfaces import CategoryQueryRepository
from shared.observability import Observability


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class CategoryQueryServiceImpl:
    def __init__(
        self,
        repo: CategoryQueryRepository,
        cache: CategoryQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetCategoriesRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("category.query.find_all", page=page, page_size=page_size):
            cached = await self._cache.get_categories(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_all(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_categories(page, page_size, search, rows, total)
            return rows, total

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetCategoriesActiveRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span(
            "category.query.find_active", page=page, page_size=page_size
        ):
            cached = await self._cache.get_active(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_active(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_active(page, page_size, search, rows, total)
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetCategoriesActiveRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span(
            "category.query.find_trashed", page=page, page_size=page_size
        ):
            cached = await self._cache.get_trashed(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_trashed(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_trashed(page, page_size, search, rows, total)
            return rows, total

    async def find_by_id(self, category_id: int) -> GetCategoryByIDRow:
        with self._obs.span("category.query.find_by_id", category_id=category_id):
            cached = await self._cache.get_category_by_id(category_id)
            if cached is not None:
                return cached
            category = await self._repo.find_by_id(category_id)
            await self._cache.set_category_by_id(category)
            return category


__all__ = ["CategoryQueryServiceImpl", "normalize_pagination"]
