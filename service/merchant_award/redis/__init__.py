"""merchant_award cache bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_award.redis.interfaces import (
    MerchantAwardCommandCache,
    MerchantAwardQueryCache,
)
from service.merchant_award.redis.merchant_award_command_cache import (
    MerchantAwardCommandCacheImpl,
)
from service.merchant_award.redis.merchant_award_query_cache import (
    MerchantAwardQueryCacheImpl,
)
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    merchant_award_query: MerchantAwardQueryCache
    merchant_award_command: MerchantAwardCommandCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        merchant_award_query=MerchantAwardQueryCacheImpl(store, logger),
        merchant_award_command=MerchantAwardCommandCacheImpl(store, logger),
    )


__all__ = [
    "Mencache",
    "MerchantAwardCommandCache",
    "MerchantAwardQueryCache",
    "new_mencache",
]
