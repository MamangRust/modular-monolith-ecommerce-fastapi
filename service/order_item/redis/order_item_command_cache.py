"""Order item command cache invalidation. clears the whole `order_item:*` namespace on every mutation (`InvalidateOrderItemCache`), which already covers the by-order key and the three list pages — so, unlike category, no per-key/list split is needed."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.order_item.redis.common import ALL_PATTERN
from shared.cache import CacheStore


class OrderItemCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def invalidate_order_item_cache(self) -> int:
        deleted = await self._store.invalidate(ALL_PATTERN)
        self._logger.debug("order item cache invalidated", keys=deleted)
        return deleted


__all__ = ["OrderItemCommandCacheImpl"]
