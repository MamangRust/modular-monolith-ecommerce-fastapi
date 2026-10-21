"""Shipping address read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip. the `WHERE ($1::TEXT IS NULL OR...)` first branch is dead: the handler always passes a non-null `search`, so an empty search matches everything through `ILIKE '%%'`. keeps only the effective predicate (same omission category/order_item document). `FindByID` / `FindByOrder` use sqlx `Get` semantics: a missing row maps to the repository's 404 error."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.shipping_address import (
    GetShippingAddressActiveRow,
    GetShippingAddressByOrderIDRow,
    GetShippingAddressRow,
    GetShippingAddressTrashedRow,
    GetShippingByIDRow,
)
from shared.errors import (
    err_find_active_shipping_address,
    err_find_all_shipping_address,
    err_find_shipping_address_by_id,
    err_find_shipping_address_by_order,
    err_find_trashed_shipping_address,
)

_GET_SHIPPING_ADDRESS = """
SELECT
    shipping_address_id,
    order_id,
    alamat,
    provinsi,
    negara,
    kota,
    courier,
    shipping_method,
    shipping_cost,
    created_at,
    updated_at,
    COUNT(*) OVER () AS total_count
FROM shipping_addresses
WHERE
    deleted_at IS NULL
    AND (
        shipping_address_id::TEXT ILIKE '%' || :search || '%'
        OR alamat ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_SHIPPING_ADDRESS_ACTIVE = """
SELECT
    shipping_address_id,
    order_id,
    alamat,
    provinsi,
    negara,
    kota,
    courier,
    shipping_method,
    shipping_cost,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM shipping_addresses
WHERE
    deleted_at IS NULL
    AND (
        shipping_address_id::TEXT ILIKE '%' || :search || '%'
        OR alamat ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_SHIPPING_ADDRESS_TRASHED = """
SELECT
    shipping_address_id,
    order_id,
    alamat,
    provinsi,
    negara,
    kota,
    courier,
    shipping_method,
    shipping_cost,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM shipping_addresses
WHERE
    deleted_at IS NOT NULL
    AND (
        shipping_address_id::TEXT ILIKE '%' || :search || '%'
        OR alamat ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_SHIPPING_BY_ID = """
SELECT
    shipping_address_id,
    order_id,
    alamat,
    provinsi,
    negara,
    kota,
    courier,
    shipping_method,
    shipping_cost,
    created_at,
    updated_at
FROM shipping_addresses
WHERE
    shipping_address_id = :shipping_id
    AND deleted_at IS NULL
"""

_GET_SHIPPING_ADDRESS_BY_ORDER_ID = """
SELECT
    shipping_address_id,
    order_id,
    alamat,
    provinsi,
    negara,
    kota,
    courier,
    shipping_method,
    shipping_cost,
    created_at,
    updated_at
FROM shipping_addresses
WHERE
    order_id = :order_id
    AND deleted_at IS NULL
"""


class ShippingAddressQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetShippingAddressRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_SHIPPING_ADDRESS,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_all_shipping_address.with_internal(exc) from exc
        return [GetShippingAddressRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetShippingAddressActiveRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_SHIPPING_ADDRESS_ACTIVE,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_active_shipping_address.with_internal(exc) from exc
        return [GetShippingAddressActiveRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetShippingAddressTrashedRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_SHIPPING_ADDRESS_TRASHED,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_trashed_shipping_address.with_internal(exc) from exc
        return [GetShippingAddressTrashedRow.from_row(row) for row in rows]

    async def find_by_id(self, shipping_id: int) -> GetShippingByIDRow:
        try:
            row = await self._db.scalar(
                _GET_SHIPPING_BY_ID, {"shipping_id": shipping_id}
            )
        except Exception as exc:
            raise err_find_shipping_address_by_id.with_internal(exc) from exc
        if row is None:
            raise err_find_shipping_address_by_id.with_internal(NoRowsError())
        return GetShippingByIDRow.from_row(row)

    async def find_by_order(self, order_id: int) -> GetShippingAddressByOrderIDRow:
        try:
            row = await self._db.scalar(
                _GET_SHIPPING_ADDRESS_BY_ORDER_ID, {"order_id": order_id}
            )
        except Exception as exc:
            raise err_find_shipping_address_by_order.with_internal(exc) from exc
        if row is None:
            raise err_find_shipping_address_by_order.with_internal(NoRowsError())
        return GetShippingAddressByOrderIDRow.from_row(row)


__all__ = ["ShippingAddressQueryRepositoryImpl"]
