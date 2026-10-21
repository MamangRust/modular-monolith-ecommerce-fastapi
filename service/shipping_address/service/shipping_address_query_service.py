"""Shipping address query service. Pagination is normalised once and the normalised values feed both the cache key and the repository call. Reads are cache-first; a miss loads from the DB and populates the cache."""

from __future__ import annotations

from pkg.database.schema.shipping_address import (
    GetShippingAddressActiveRow,
    GetShippingAddressByOrderIDRow,
    GetShippingAddressRow,
    GetShippingAddressTrashedRow,
    GetShippingByIDRow,
)
from pkg.logger.logger import Logger
from service.shipping_address.redis.interfaces import ShippingAddressQueryCache
from service.shipping_address.repository.interfaces import (
    ShippingAddressQueryRepository,
)
from shared.errors import (
    err_failed_find_active_shipping_addresses,
    err_failed_find_all_shipping_addresses,
    err_failed_find_trashed_shipping_addresses,
)
from shared.observability import Observability


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class ShippingAddressQueryServiceImpl:
    def __init__(
        self,
        repo: ShippingAddressQueryRepository,
        cache: ShippingAddressQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetShippingAddressRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span(
            "shipping_address.query.find_all", page=page, page_size=page_size
        ):
            cached = await self._cache.get_shipping_address_all(
                page, page_size, search
            )
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_all(search, page, page_size)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to find all shipping addresses: {exc}")
                raise err_failed_find_all_shipping_addresses from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_shipping_address_all(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetShippingAddressActiveRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span(
            "shipping_address.query.find_active", page=page, page_size=page_size
        ):
            cached = await self._cache.get_shipping_address_active(
                page, page_size, search
            )
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_active(search, page, page_size)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to find active shipping addresses: {exc}")
                raise err_failed_find_active_shipping_addresses from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_shipping_address_active(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetShippingAddressTrashedRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span(
            "shipping_address.query.find_trashed", page=page, page_size=page_size
        ):
            cached = await self._cache.get_shipping_address_trashed(
                page, page_size, search
            )
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_trashed(search, page, page_size)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to find trashed shipping addresses: {exc}")
                raise err_failed_find_trashed_shipping_addresses from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_shipping_address_trashed(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_by_id(self, shipping_id: int) -> GetShippingByIDRow:
        with self._obs.span(
            "shipping_address.query.find_by_id", shipping_id=shipping_id
        ):
            cached = await self._cache.get_cached_shipping_address(shipping_id)
            if cached is not None:
                return cached
            # Propagated as-is: a missing row is the repository's 404.
            row = await self._repo.find_by_id(shipping_id)
            await self._cache.set_cached_shipping_address(row)
            return row

    async def find_by_order(self, order_id: int) -> GetShippingAddressByOrderIDRow:
        with self._obs.span(
            "shipping_address.query.find_by_order", order_id=order_id
        ):
            cached = await self._cache.get_cached_shipping_address_by_order(order_id)
            if cached is not None:
                return cached
            # Propagated as-is: a missing row is the repository's 404.
            row = await self._repo.find_by_order(order_id)
            await self._cache.set_cached_shipping_address_by_order(row)
            return row


__all__ = ["ShippingAddressQueryServiceImpl", "normalize_pagination"]
