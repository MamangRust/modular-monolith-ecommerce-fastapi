"""merchant_business command cache invalidation."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.merchant_business.redis.common import merchant_business_by_id_key
from shared.cache import CacheStore


class MerchantBusinessCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_merchant_business(
        self, merchant_business_info_id: int
    ) -> int:
        return await self._store.delete(
            merchant_business_by_id_key(merchant_business_info_id)
        )


__all__ = ["MerchantBusinessCommandCacheImpl"]
