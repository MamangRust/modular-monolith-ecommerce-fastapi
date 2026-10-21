"""Category command cache invalidation. Deviation from (recorded in the): only dropped `category:id:<id>` on Update/Trash/Restore/DeletePermanent and never invalidated lists (Create/RestoreAll/DeleteAll cleared nothing), leaving stale list pages for up to 5 minutes. invalidates by-id plus every list pattern after the mutation has committed — the same rule the role/user/banner. Stats caches are deliberately left alone, matching (stats depend on orders, not on category writes)."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.category.redis.common import LIST_PATTERNS, category_by_id_key
from shared.cache import CacheStore

CATEGORY_ID_PATTERN = "category:id:*"


class CategoryCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_category(self, category_id: int) -> int:
        return await self._store.delete(category_by_id_key(category_id))

    async def invalidate_lists(self) -> int:
        deleted = 0
        for pattern in LIST_PATTERNS:
            deleted += await self._store.invalidate(pattern)
        return deleted

    async def invalidate_category(self, category_id: int) -> int:
        deleted = await self.delete_cached_category(category_id)
        deleted += await self.invalidate_lists()
        self._logger.debug(
            "category cache invalidated", category_id=category_id, keys=deleted
        )
        return deleted

    async def invalidate_all(self) -> int:
        deleted = await self._store.invalidate(CATEGORY_ID_PATTERN)
        deleted += await self.invalidate_lists()
        self._logger.debug("category cache fully invalidated", keys=deleted)
        return deleted


__all__ = ["CategoryCommandCacheImpl"]
