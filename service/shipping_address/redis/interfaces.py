"""Shipping address cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.shipping_address import (
    GetShippingAddressActiveRow,
    GetShippingAddressByOrderIDRow,
    GetShippingAddressRow,
    GetShippingAddressTrashedRow,
    GetShippingByIDRow,
)


class ShippingAddressQueryCache(Protocol):
    async def get_shipping_address_all(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetShippingAddressRow], int] | None: ...

    async def set_shipping_address_all(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetShippingAddressRow],
        total: int,
    ) -> None: ...

    async def get_shipping_address_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetShippingAddressActiveRow], int] | None: ...

    async def set_shipping_address_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetShippingAddressActiveRow],
        total: int,
    ) -> None: ...

    async def get_shipping_address_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetShippingAddressTrashedRow], int] | None: ...

    async def set_shipping_address_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetShippingAddressTrashedRow],
        total: int,
    ) -> None: ...

    async def get_cached_shipping_address(
        self, shipping_id: int
    ) -> GetShippingByIDRow | None: ...

    async def set_cached_shipping_address(self, row: GetShippingByIDRow) -> None: ...

    async def get_cached_shipping_address_by_order(
        self, order_id: int
    ) -> GetShippingAddressByOrderIDRow | None: ...

    async def set_cached_shipping_address_by_order(
        self, row: GetShippingAddressByOrderIDRow
    ) -> None: ...


class ShippingAddressCommandCache(Protocol):
    async def delete_shipping_address_cache(self, shipping_id: int) -> int: ...

    async def invalidate_shipping_address_cache(self) -> int: ...


__all__ = ["ShippingAddressCommandCache", "ShippingAddressQueryCache"]
