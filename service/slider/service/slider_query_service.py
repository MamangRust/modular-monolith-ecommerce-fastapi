"""Slider query service. Pagination is normalised once and the normalised values are used for both the cache key and the repository call. Reads are cache-first; a miss loads from the DB and populates the cache. Repository failures are propagated unchanged (the service forwards them through `errorhandler.HandleError`, which returns the `AppError`), so the wire code matches the repository error — a DB error during `find_all` surfaces as the repository's 404 `failed to find all sliders`, not a 500."""

from __future__ import annotations

from pkg.database.schema.slider import (
    GetSliderByIDRow,
    GetSlidersActiveRow,
    GetSlidersRow,
)
from pkg.logger.logger import Logger
from service.slider.redis.interfaces import SliderQueryCache
from service.slider.repository.interfaces import SliderQueryRepository
from shared.observability import Observability


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class SliderQueryServiceImpl:
    def __init__(
        self,
        repo: SliderQueryRepository,
        cache: SliderQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetSlidersRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("slider.query.find_all", page=page, page_size=page_size):
            cached = await self._cache.get_sliders(page, page_size, search)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_all(search, page, page_size)
            except Exception as exc:
                self._logger.error("failed to fetch sliders", error=str(exc))
                raise
            total = rows[0].total_count if rows else 0
            await self._cache.set_sliders(page, page_size, search, rows, total)
            return rows, total

    async def find_by_id(self, slider_id: int) -> GetSliderByIDRow:
        with self._obs.span("slider.query.find_by_id", slider_id=slider_id):
            cached = await self._cache.get_slider_by_id(slider_id)
            if cached is not None:
                return cached
            slider = await self._repo.find_by_id(slider_id)
            await self._cache.set_slider_by_id(slider)
            return slider

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetSlidersActiveRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("slider.query.find_active", page=page, page_size=page_size):
            cached = await self._cache.get_active(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_active(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_active(page, page_size, search, rows, total)
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetSlidersActiveRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("slider.query.find_trashed", page=page, page_size=page_size):
            cached = await self._cache.get_trashed(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_trashed(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_trashed(page, page_size, search, rows, total)
            return rows, total


__all__ = ["SliderQueryServiceImpl", "normalize_pagination"]
