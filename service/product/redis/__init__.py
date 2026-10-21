"""product cache bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.product.redis.interfaces import (
    ProductCommandCache,
    ProductQueryCache,
)
from service.product.redis.product_command_cache import ProductCommandCacheImpl
from service.product.redis.product_query_cache import ProductQueryCacheImpl
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    product_query: ProductQueryCache
    product_command: ProductCommandCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        product_query=ProductQueryCacheImpl(store, logger),
        product_command=ProductCommandCacheImpl(store, logger),
    )


__all__ = [
    "Mencache",
    "ProductCommandCache",
    "ProductQueryCache",
    "new_mencache",
]
