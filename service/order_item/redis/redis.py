"""Order item cache composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.order_item.redis.interfaces import (
    OrderItemCommandCache,
    OrderItemQueryCache,
)
from service.order_item.redis.order_item_command_cache import (
    OrderItemCommandCacheImpl,
)
from service.order_item.redis.order_item_query_cache import OrderItemQueryCacheImpl
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    query: OrderItemQueryCache
    command: OrderItemCommandCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        query=OrderItemQueryCacheImpl(store, logger),
        command=OrderItemCommandCacheImpl(store, logger),
    )


__all__ = ["Mencache", "new_mencache"]
