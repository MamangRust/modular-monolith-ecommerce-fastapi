"""Merchant document command cache invalidation."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.merchant.redis.common import merchant_document_by_id_key
from shared.cache import CacheStore


class MerchantDocumentCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_merchant_documents(self, document_id: int) -> int:
        return await self._store.delete(merchant_document_by_id_key(document_id))


__all__ = ["MerchantDocumentCommandCacheImpl"]
