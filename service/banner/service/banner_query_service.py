"""Banner query service.

Pagination is normalised once and the normalised values are used for both
the cache key and the repository call. Reads are cache-first; a miss loads
from the DB and populates the cache."""

from __future__ import annotations

from pkg.database.schema.banner import (
    GetBannerRow,
    GetBannersActiveRow,
    GetBannersRow,
)
from pkg.logger.logger import Logger
from service.banner.redis.interfaces import BannerQueryCache
from service.banner.repository.interfaces import BannerQueryRepository
from shared.observability import Observability


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class BannerQueryServiceImpl:
    def __init__(
        self,
        repo: BannerQueryRepository,
        cache: BannerQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetBannersRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("banner.query.find_all", page=page, page_size=page_size):
            cached = await self._cache.get_banners(page, page_size, search)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_all(search, page, page_size)
            except Exception as exc:
                self._logger.error("failed to fetch banners", error=str(exc))
                raise
            total = rows[0].total_count if rows else 0
            await self._cache.set_banners(page, page_size, search, rows, total)
            return rows, total

    async def find_by_id(self, banner_id: int) -> GetBannerRow:
        with self._obs.span("banner.query.find_by_id", banner_id=banner_id):
            cached = await self._cache.get_banner_by_id(banner_id)
            if cached is not None:
                return cached
            banner = await self._repo.find_by_id(banner_id)
            await self._cache.set_banner_by_id(banner)
            return banner

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetBannersActiveRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("banner.query.find_active", page=page, page_size=page_size):
            cached = await self._cache.get_active(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_active(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_active(page, page_size, search, rows, total)
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetBannersActiveRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("banner.query.find_trashed", page=page, page_size=page_size):
            cached = await self._cache.get_trashed(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_trashed(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_trashed(page, page_size, search, rows, total)
            return rows, total


__all__ = ["BannerQueryServiceImpl", "normalize_pagination"]
