"""Merchant cache bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant.redis.interfaces import (
    MerchantCommandCache,
    MerchantDocumentCommandCache,
    MerchantDocumentQueryCache,
    MerchantQueryCache,
)
from service.merchant.redis.merchant_command_cache import MerchantCommandCacheImpl
from service.merchant.redis.merchant_document_command_cache import (
    MerchantDocumentCommandCacheImpl,
)
from service.merchant.redis.merchant_document_query_cache import (
    MerchantDocumentQueryCacheImpl,
)
from service.merchant.redis.merchant_query_cache import MerchantQueryCacheImpl
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    merchant_query: MerchantQueryCache
    merchant_command: MerchantCommandCache
    merchant_document_query: MerchantDocumentQueryCache
    merchant_document_command: MerchantDocumentCommandCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        merchant_query=MerchantQueryCacheImpl(store, logger),
        merchant_command=MerchantCommandCacheImpl(store, logger),
        merchant_document_query=MerchantDocumentQueryCacheImpl(store, logger),
        merchant_document_command=MerchantDocumentCommandCacheImpl(store, logger),
    )


__all__ = [
    "Mencache",
    "MerchantCommandCache",
    "MerchantDocumentCommandCache",
    "MerchantDocumentQueryCache",
    "MerchantQueryCache",
    "new_mencache",
]
