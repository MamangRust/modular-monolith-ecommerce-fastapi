"""merchant_detail cache bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_detail.redis.interfaces import (
    MerchantDetailCommandCache,
    MerchantDetailQueryCache,
)
from service.merchant_detail.redis.merchant_detail_command_cache import (
    MerchantDetailCommandCacheImpl,
)
from service.merchant_detail.redis.merchant_detail_query_cache import (
    MerchantDetailQueryCacheImpl,
)
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    merchant_detail_query: MerchantDetailQueryCache
    merchant_detail_command: MerchantDetailCommandCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        merchant_detail_query=MerchantDetailQueryCacheImpl(store, logger),
        merchant_detail_command=MerchantDetailCommandCacheImpl(store, logger),
    )


__all__ = [
    "Mencache",
    "MerchantDetailCommandCache",
    "MerchantDetailQueryCache",
    "new_mencache",
]
