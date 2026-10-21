"""Shipping address cache composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.shipping_address.redis.interfaces import (
    ShippingAddressCommandCache,
    ShippingAddressQueryCache,
)
from service.shipping_address.redis.shipping_address_command_cache import (
    ShippingAddressCommandCacheImpl,
)
from service.shipping_address.redis.shipping_address_query_cache import (
    ShippingAddressQueryCacheImpl,
)
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    query: ShippingAddressQueryCache
    command: ShippingAddressCommandCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        query=ShippingAddressQueryCacheImpl(store, logger),
        command=ShippingAddressCommandCacheImpl(store, logger),
    )


__all__ = ["Mencache", "new_mencache"]
