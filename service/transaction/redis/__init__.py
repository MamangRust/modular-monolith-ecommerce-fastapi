"""transaction cache bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.transaction.redis.interfaces import (
    TransactionCommandCache,
    TransactionQueryCache,
    TransactionStatsByMerchantCache,
    TransactionStatsCache,
)
from service.transaction.redis.transaction_command_cache import (
    TransactionCommandCacheImpl,
)
from service.transaction.redis.transaction_query_cache import (
    TransactionQueryCacheImpl,
)
from service.transaction.redis.transaction_stats_by_merchant_cache import (
    TransactionStatsByMerchantCacheImpl,
)
from service.transaction.redis.transaction_stats_cache import (
    TransactionStatsCacheImpl,
)
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    transaction_query: TransactionQueryCache
    transaction_command: TransactionCommandCache
    transaction_stats: TransactionStatsCache
    transaction_stats_by_merchant: TransactionStatsByMerchantCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        transaction_query=TransactionQueryCacheImpl(store, logger),
        transaction_command=TransactionCommandCacheImpl(store, logger),
        transaction_stats=TransactionStatsCacheImpl(store, logger),
        transaction_stats_by_merchant=TransactionStatsByMerchantCacheImpl(store, logger),
    )


__all__ = [
    "Mencache",
    "TransactionCommandCache",
    "TransactionQueryCache",
    "TransactionStatsByMerchantCache",
    "TransactionStatsCache",
    "new_mencache",
]
