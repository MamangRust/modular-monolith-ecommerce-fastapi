"""merchant_award command cache invalidation. `Update`/`Trash`/`DeletePermanent` evict the by-id key (`Restore` and the bulk operations do not)."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.merchant_award.redis.common import merchant_award_by_id_key
from shared.cache import CacheStore


class MerchantAwardCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_merchant_award(
        self, merchant_certification_id: int
    ) -> int:
        return await self._store.delete(
            merchant_award_by_id_key(merchant_certification_id)
        )


__all__ = ["MerchantAwardCommandCacheImpl"]
