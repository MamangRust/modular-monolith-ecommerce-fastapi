"""Merchant command cache invalidation. Single mutations evict the by-id key; `invalidate_merchant_cache` flushes the whole `merchant:*` namespace (`InvalidateCache(ctx, "merchant:*")`)."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.merchant.redis.common import MERCHANT_ALL_PATTERN, merchant_by_id_key
from shared.cache import CacheStore


class MerchantCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_merchant(self, merchant_id: int) -> int:
        return await self._store.delete(merchant_by_id_key(merchant_id))

    async def invalidate_merchant_cache(self) -> int:
        return await self._store.invalidate(MERCHANT_ALL_PATTERN)


__all__ = ["MerchantCommandCacheImpl"]
