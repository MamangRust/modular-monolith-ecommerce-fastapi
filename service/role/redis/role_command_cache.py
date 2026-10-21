"""Role command cache invalidation. Deviation from (recorded in the matrix): defined `DeleteCachedRole` but never called it, so every mutation left stale `role:id:*` and list entries for up to 5 minutes. invalidates after the mutation has committed — by-id, list and by-user keys — so a write is immediately visible."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.role.redis.common import LIST_PATTERNS, role_by_id_key
from shared.cache import CacheStore

ROLE_ID_PATTERN = "role:id:*"


class RoleCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_role(self, role_id: int) -> int:
        return await self._store.delete(role_by_id_key(role_id))

    async def invalidate_lists(self) -> int:
        deleted = 0
        for pattern in LIST_PATTERNS:
            deleted += await self._store.invalidate(pattern)
        return deleted

    async def invalidate_role(self, role_id: int) -> int:
        deleted = await self.delete_cached_role(role_id)
        deleted += await self.invalidate_lists()
        self._logger.debug("role cache invalidated", role_id=role_id, keys=deleted)
        return deleted

    async def invalidate_all(self) -> int:
        deleted = await self._store.invalidate(ROLE_ID_PATTERN)
        deleted += await self.invalidate_lists()
        self._logger.debug("role cache fully invalidated", keys=deleted)
        return deleted


__all__ = ["RoleCommandCacheImpl"]
