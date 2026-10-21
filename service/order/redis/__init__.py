"""order cache bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.order.redis.interfaces import (
    OrderCommandCache,
    OrderQueryCache,
    OrderStatsByMerchantCache,
    OrderStatsCache,
)
from service.order.redis.order_command_cache import OrderCommandCacheImpl
from service.order.redis.order_query_cache import OrderQueryCacheImpl
from service.order.redis.order_stats_by_merchant_cache import (
    OrderStatsByMerchantCacheImpl,
)
from service.order.redis.order_stats_cache import OrderStatsCacheImpl
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    order_query: OrderQueryCache
    order_command: OrderCommandCache
    order_stats: OrderStatsCache
    order_stats_by_merchant: OrderStatsByMerchantCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        order_query=OrderQueryCacheImpl(store, logger),
        order_command=OrderCommandCacheImpl(store, logger),
        order_stats=OrderStatsCacheImpl(store, logger),
        order_stats_by_merchant=OrderStatsByMerchantCacheImpl(store, logger),
    )


__all__ = [
    "Mencache",
    "OrderCommandCache",
    "OrderQueryCache",
    "OrderStatsByMerchantCache",
    "OrderStatsCache",
    "new_mencache",
]
