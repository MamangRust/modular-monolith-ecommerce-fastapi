"""cart command cache invalidation. A cart mutation (create/delete/delete-all) invalidates every cached listing for that user so no stale page is served. logs an error when the pattern invalidation fails; `CacheStore.invalidate` swallows Redis errors and returns the match count, so simply returns it."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.cart.redis.common import cart_user_pattern
from shared.cache import CacheStore


class CartCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_carts(self, user_id: int) -> int:
        return await self._store.invalidate(cart_user_pattern(user_id))


__all__ = ["CartCommandCacheImpl"]
