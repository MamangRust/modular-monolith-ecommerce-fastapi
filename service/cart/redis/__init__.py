"""cart cache bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.cart.redis.cart_command_cache import CartCommandCacheImpl
from service.cart.redis.cart_query_cache import CartQueryCacheImpl
from service.cart.redis.interfaces import (
    CartCommandCache,
    CartQueryCache,
)
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    cart_query: CartQueryCache
    cart_command: CartCommandCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        cart_query=CartQueryCacheImpl(store, logger),
        cart_command=CartCommandCacheImpl(store, logger),
    )


__all__ = [
    "CartCommandCache",
    "CartQueryCache",
    "Mencache",
    "new_mencache",
]
