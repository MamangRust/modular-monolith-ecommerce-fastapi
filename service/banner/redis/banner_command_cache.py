"""Banner command cache invalidation. Deviation from (recorded in the matrix): only dropped `banner:id:*` on Update/Trash/Restore/DeletePermanent and never invalidated lists (Create/RestoreAll/DeleteAll cleared nothing), leaving stale list pages for up to 5 minutes. invalidates by-id plus every list pattern after the mutation has committed — the same rule the role/user."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.banner.redis.common import LIST_PATTERNS, banner_by_id_key
from shared.cache import CacheStore

BANNER_ID_PATTERN = "banner:id:*"


class BannerCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_banner(self, banner_id: int) -> int:
        return await self._store.delete(banner_by_id_key(banner_id))

    async def invalidate_lists(self) -> int:
        deleted = 0
        for pattern in LIST_PATTERNS:
            deleted += await self._store.invalidate(pattern)
        return deleted

    async def invalidate_banner(self, banner_id: int) -> int:
        deleted = await self.delete_cached_banner(banner_id)
        deleted += await self.invalidate_lists()
        self._logger.debug("banner cache invalidated", banner_id=banner_id, keys=deleted)
        return deleted

    async def invalidate_all(self) -> int:
        deleted = await self._store.invalidate(BANNER_ID_PATTERN)
        deleted += await self.invalidate_lists()
        self._logger.debug("banner cache fully invalidated", keys=deleted)
        return deleted


__all__ = ["BannerCommandCacheImpl"]
