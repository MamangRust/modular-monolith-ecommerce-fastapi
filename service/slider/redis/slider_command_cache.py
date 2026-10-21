"""Slider command cache invalidation. flushes the entire `slider:*` namespace on every mutation (Create/Update/ Trash/Restore/DeletePermanent/RestoreAll/DeleteAll), so single wildcard invalidation rather than the selective by-id + list approach the banner port uses."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.slider.redis.common import SLIDER_ALL_PATTERN
from shared.cache import CacheStore


class SliderCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_slider_cache(self, slider_id: int) -> int:
        return await self._store.invalidate(SLIDER_ALL_PATTERN)

    async def invalidate_slider_cache(self) -> int:
        return await self._store.invalidate(SLIDER_ALL_PATTERN)


__all__ = ["SliderCommandCacheImpl"]
