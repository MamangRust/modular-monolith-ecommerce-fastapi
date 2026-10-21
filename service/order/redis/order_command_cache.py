"""order command cache invalidation. NORMALISATION: `DeleteOrderCache` invalidates `order:*` and, only when that returns an error, falls back to deleting the single `order:id:%d` key; `InvalidateOrderCache` invalidates `order:*` and logs on error. The Python `CacheStore.invalidate` swallows Redis errors and returns the deleted-key count, so there is no error branch to take. therefore invalidates the whole `order:*` namespace in both methods, matching happy path. The `order_id` argument is kept for signature."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.order.redis.common import ORDER_NAMESPACE_PATTERN
from shared.cache import CacheStore


class OrderCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_order_cache(self, order_id: int) -> int:
        return await self._store.invalidate(ORDER_NAMESPACE_PATTERN)

    async def invalidate_order_cache(self) -> int:
        return await self._store.invalidate(ORDER_NAMESPACE_PATTERN)


__all__ = ["OrderCommandCacheImpl"]
