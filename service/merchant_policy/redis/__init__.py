"""merchant_policy cache bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_policy.redis.interfaces import (
    MerchantPolicyCommandCache,
    MerchantPolicyQueryCache,
)
from service.merchant_policy.redis.merchant_policy_command_cache import (
    MerchantPolicyCommandCacheImpl,
)
from service.merchant_policy.redis.merchant_policy_query_cache import (
    MerchantPolicyQueryCacheImpl,
)
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    merchant_policy_query: MerchantPolicyQueryCache
    merchant_policy_command: MerchantPolicyCommandCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        merchant_policy_query=MerchantPolicyQueryCacheImpl(store, logger),
        merchant_policy_command=MerchantPolicyCommandCacheImpl(store, logger),
    )


__all__ = [
    "Mencache",
    "MerchantPolicyCommandCache",
    "MerchantPolicyQueryCache",
    "new_mencache",
]
