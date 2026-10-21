"""Shipping address command cache invalidation. exposes two operations: a by-id delete (`DeleteShippingAddressCache`, used by the gateway's own cache) and a whole-namespace invalidation (`InvalidateShippingAddressCache`, used by the domain service after every mutation). keeps both; the domain service calls the pattern invalidation."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.shipping_address.redis.common import (
    ALL_PATTERN,
    shipping_address_by_id_key,
)
from shared.cache import CacheStore


class ShippingAddressCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_shipping_address_cache(self, shipping_id: int) -> int:
        deleted = await self._store.delete(shipping_address_by_id_key(shipping_id))
        self._logger.debug(
            "shipping address cache deleted", shipping_id=shipping_id, keys=deleted
        )
        return deleted

    async def invalidate_shipping_address_cache(self) -> int:
        deleted = await self._store.invalidate(ALL_PATTERN)
        self._logger.debug("shipping address cache invalidated", keys=deleted)
        return deleted


__all__ = ["ShippingAddressCommandCacheImpl"]
