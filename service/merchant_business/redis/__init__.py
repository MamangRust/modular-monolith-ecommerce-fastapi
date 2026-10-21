"""merchant_business cache bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_business.redis.interfaces import (
    MerchantBusinessCommandCache,
    MerchantBusinessQueryCache,
)
from service.merchant_business.redis.merchant_business_command_cache import (
    MerchantBusinessCommandCacheImpl,
)
from service.merchant_business.redis.merchant_business_query_cache import (
    MerchantBusinessQueryCacheImpl,
)
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    merchant_business_query: MerchantBusinessQueryCache
    merchant_business_command: MerchantBusinessCommandCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        merchant_business_query=MerchantBusinessQueryCacheImpl(store, logger),
        merchant_business_command=MerchantBusinessCommandCacheImpl(store, logger),
    )


__all__ = [
    "Mencache",
    "MerchantBusinessCommandCache",
    "MerchantBusinessQueryCache",
    "new_mencache",
]
