"""merchant_detail command cache invalidation.

Every mutation (update/trash/restore/delete) evicts the by-id key."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.merchant_detail.redis.common import merchant_detail_by_id_key
from shared.cache import CacheStore


class MerchantDetailCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_merchant_detail(self, merchant_detail_id: int) -> int:
        return await self._store.delete(
            merchant_detail_by_id_key(merchant_detail_id)
        )


__all__ = ["MerchantDetailCommandCacheImpl"]
