"""User command cache invalidation. Unlike the role service, the user service does invoke its cache on every mutation, so no deviation is needed here: by-id is dropped for single-row operations and all list pages for every write."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.user.redis.common import LIST_PATTERNS, user_by_id_key
from shared.cache import CacheStore

USER_ID_PATTERN = "user:id:*"


class UserCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_user(self, user_id: int) -> int:
        return await self._store.delete(user_by_id_key(user_id))

    async def invalidate_lists(self) -> int:
        deleted = 0
        for pattern in LIST_PATTERNS:
            deleted += await self._store.invalidate(pattern)
        return deleted

    async def invalidate_user(self, user_id: int) -> int:
        deleted = await self.delete_cached_user(user_id)
        deleted += await self.invalidate_lists()
        self._logger.debug("user cache invalidated", user_id=user_id, keys=deleted)
        return deleted

    async def invalidate_all(self) -> int:
        deleted = await self._store.invalidate(USER_ID_PATTERN)
        deleted += await self.invalidate_lists()
        self._logger.debug("user cache fully invalidated", keys=deleted)
        return deleted


__all__ = ["UserCommandCacheImpl"]
