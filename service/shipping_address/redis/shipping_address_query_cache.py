"""Shipping address query cache. Reads/writes never raise: `CacheStore` swallows Redis errors so a cache outage degrades to a DB read. The by-id/by-order setters skip a nil row (returns early when `data == nil`)."""

from __future__ import annotations

from pkg.database.schema.shipping_address import (
    GetShippingAddressActiveRow,
    GetShippingAddressByOrderIDRow,
    GetShippingAddressRow,
    GetShippingAddressTrashedRow,
    GetShippingByIDRow,
)
from pkg.logger.logger import Logger
from service.shipping_address.redis.cache import (
    active_row_from_dict,
    active_row_to_dict,
    by_id_row_from_dict,
    by_id_row_to_dict,
    by_order_row_from_dict,
    by_order_row_to_dict,
    shipping_row_from_dict,
    shipping_row_to_dict,
)
from service.shipping_address.redis.common import (
    TTL_DEFAULT,
    shipping_address_active_key,
    shipping_address_all_key,
    shipping_address_by_id_key,
    shipping_address_by_order_key,
    shipping_address_trashed_key,
)
from shared.cache import CacheStore


class ShippingAddressQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_shipping_address_all(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetShippingAddressRow], int] | None:
        payload = await self._store.get_json(
            shipping_address_all_key(page, page_size, search)
        )
        return _decode_page(payload, shipping_row_from_dict)

    async def set_shipping_address_all(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetShippingAddressRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            shipping_address_all_key(page, page_size, search),
            _encode_page(rows, total, shipping_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_shipping_address_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetShippingAddressActiveRow], int] | None:
        payload = await self._store.get_json(
            shipping_address_active_key(page, page_size, search)
        )
        return _decode_page(payload, active_row_from_dict)

    async def set_shipping_address_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetShippingAddressActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            shipping_address_active_key(page, page_size, search),
            _encode_page(rows, total, active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_shipping_address_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetShippingAddressTrashedRow], int] | None:
        payload = await self._store.get_json(
            shipping_address_trashed_key(page, page_size, search)
        )
        return _decode_page(payload, active_row_from_dict)

    async def set_shipping_address_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetShippingAddressTrashedRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            shipping_address_trashed_key(page, page_size, search),
            _encode_page(rows, total, active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_cached_shipping_address(
        self, shipping_id: int
    ) -> GetShippingByIDRow | None:
        payload = await self._store.get_json(
            shipping_address_by_id_key(shipping_id)
        )
        if not isinstance(payload, dict):
            return None
        return by_id_row_from_dict(payload)

    async def set_cached_shipping_address(self, row: GetShippingByIDRow) -> None:
        if row is None:
            return
        await self._store.set_json(
            shipping_address_by_id_key(row.shipping_address_id),
            by_id_row_to_dict(row),
            TTL_DEFAULT,
        )

    async def get_cached_shipping_address_by_order(
        self, order_id: int
    ) -> GetShippingAddressByOrderIDRow | None:
        payload = await self._store.get_json(
            shipping_address_by_order_key(order_id)
        )
        if not isinstance(payload, dict):
            return None
        return by_order_row_from_dict(payload)

    async def set_cached_shipping_address_by_order(
        self, row: GetShippingAddressByOrderIDRow
    ) -> None:
        if row is None:
            return
        await self._store.set_json(
            shipping_address_by_order_key(row.order_id),
            by_order_row_to_dict(row),
            TTL_DEFAULT,
        )


def _encode_page(rows: list, total: int, to_dict) -> dict:
    return {"data": [to_dict(row) for row in rows], "total_records": total}


def _decode_page(payload, from_dict):
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    total = int(payload.get("total_records") or 0)
    return [from_dict(item, total) for item in data], total


__all__ = ["ShippingAddressQueryCacheImpl"]
