"""merchant_policy command cache invalidation."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.merchant_policy.redis.common import merchant_policy_by_id_key
from shared.cache import CacheStore


class MerchantPolicyCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_merchant_policy(self, merchant_policy_id: int) -> int:
        return await self._store.delete(
            merchant_policy_by_id_key(merchant_policy_id)
        )


__all__ = ["MerchantPolicyCommandCacheImpl"]
