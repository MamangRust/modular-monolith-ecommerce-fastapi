"""Shipping address repository"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.shipping_address import (
    CreateShippingAddressRow,
    GetShippingAddressActiveRow,
    GetShippingAddressByOrderIDRow,
    GetShippingAddressRow,
    GetShippingAddressTrashedRow,
    GetShippingByIDRow,
    ShippingAddress,
    UpdateShippingAddressRow,
)
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)


class ShippingAddressQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetShippingAddressRow]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetShippingAddressActiveRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetShippingAddressTrashedRow]: ...

    async def find_by_id(self, shipping_id: int) -> GetShippingByIDRow: ...

    async def find_by_order(self, order_id: int) -> GetShippingAddressByOrderIDRow: ...


class ShippingAddressCommandRepository(Protocol):
    async def create(
        self, request: CreateShippingAddressRequest
    ) -> CreateShippingAddressRow: ...

    async def update(
        self, request: UpdateShippingAddressRequest
    ) -> UpdateShippingAddressRow: ...

    async def trash(self, shipping_id: int) -> ShippingAddress: ...

    async def restore(self, shipping_id: int) -> ShippingAddress: ...

    async def delete_permanent(self, shipping_id: int) -> bool: ...

    async def delete_by_order_id_permanent(self, order_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


__all__ = ["ShippingAddressCommandRepository", "ShippingAddressQueryRepository"]
