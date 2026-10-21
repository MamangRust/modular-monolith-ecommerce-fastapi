"""Shipping address write repository. Soft delete uses `deleted_at`; the permanent deletes are hard deletes. `create`/`update` return the raw driver error in (the service replaces it with its own sentinel); raises a wrapped AppError defensively, and the service still overrides it, so the wire result matches. `delete_by_order_id_permanent` purges every address of an order regardless of `deleted_at` (used by the order compensation path); `delete_all` additionally clears addresses whose parent order is trashed."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.shipping_address import (
    CreateShippingAddressRow,
    ShippingAddress,
    UpdateShippingAddressRow,
)
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)
from shared.errors import (
    AppError,
    err_create_shipping_address,
    err_delete_all_permanent_shipping_address,
    err_delete_shipping_address_permanent,
    err_restore_all_shipping_addresses,
    err_restore_shipping_address,
    err_shipping_address_not_found,
    err_trash_shipping_address,
    err_update_shipping_address,
)

_CREATE_SHIPPING_ADDRESS = """
INSERT INTO shipping_addresses (
    order_id,
    alamat,
    provinsi,
    negara,
    kota,
    courier,
    shipping_method,
    shipping_cost
)
VALUES (
    :order_id,
    :alamat,
    :provinsi,
    :negara,
    :kota,
    :courier,
    :shipping_method,
    :shipping_cost
)
RETURNING
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
"""

_UPDATE_SHIPPING_ADDRESS = """
UPDATE shipping_addresses
SET
    alamat = :alamat,
    provinsi = :provinsi,
    negara = :negara,
    kota = :kota,
    courier = :courier,
    shipping_method = :shipping_method,
    shipping_cost = :shipping_cost,
    updated_at = CURRENT_TIMESTAMP
WHERE
    shipping_address_id = :shipping_id
    AND deleted_at IS NULL
RETURNING
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
"""

_TRASH_SHIPPING_ADDRESS = """
UPDATE shipping_addresses
SET deleted_at = CURRENT_TIMESTAMP
WHERE
    shipping_address_id = :shipping_id
    AND deleted_at IS NULL
RETURNING
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
    deleted_at
"""

_RESTORE_SHIPPING_ADDRESS = """
UPDATE shipping_addresses
SET deleted_at = NULL
WHERE
    shipping_address_id = :shipping_id
    AND deleted_at IS NOT NULL
RETURNING
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
    deleted_at
"""

_DELETE_SHIPPING_ADDRESS_PERMANENTLY = """
DELETE FROM shipping_addresses
WHERE
    shipping_address_id = :shipping_id
    AND deleted_at IS NOT NULL
"""

_DELETE_SHIPPING_ADDRESS_BY_ORDER_PERMANENT = (
    "DELETE FROM shipping_addresses WHERE order_id = :order_id"
)

_RESTORE_ALL_SHIPPING_ADDRESS = (
    "UPDATE shipping_addresses SET deleted_at = NULL WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_PERMANENT_SHIPPING_ADDRESS = """
DELETE FROM shipping_addresses
WHERE
    deleted_at IS NOT NULL
    OR order_id IN (SELECT order_id FROM orders WHERE deleted_at IS NOT NULL)
"""


class ShippingAddressCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(
        self, request: CreateShippingAddressRequest
    ) -> CreateShippingAddressRow:
        params = {
            "order_id": request.order_id,
            "alamat": request.alamat,
            "provinsi": request.provinsi,
            "negara": request.negara,
            "kota": request.kota,
            "courier": request.courier,
            "shipping_method": request.shipping_method,
            "shipping_cost": request.shipping_cost,
        }
        try:
            row = await self._db.execute(_CREATE_SHIPPING_ADDRESS, params)
        except Exception as exc:
            raise err_create_shipping_address.with_internal(exc) from exc
        if row is None:
            raise err_shipping_address_not_found.with_internal(NoRowsError())
        return CreateShippingAddressRow.from_row(row)

    async def update(
        self, request: UpdateShippingAddressRequest
    ) -> UpdateShippingAddressRow:
        params = {
            "shipping_id": request.shipping_id,
            "alamat": request.alamat,
            "provinsi": request.provinsi,
            "negara": request.negara,
            "kota": request.kota,
            "courier": request.courier,
            "shipping_method": request.shipping_method,
            "shipping_cost": request.shipping_cost,
        }
        try:
            row = await self._db.execute(_UPDATE_SHIPPING_ADDRESS, params)
        except Exception as exc:
            raise err_update_shipping_address.with_internal(exc) from exc
        if row is None:
            raise err_shipping_address_not_found.with_internal(NoRowsError())
        return UpdateShippingAddressRow.from_row(row)

    async def trash(self, shipping_id: int) -> ShippingAddress:
        try:
            row = await self._db.execute(
                _TRASH_SHIPPING_ADDRESS, {"shipping_id": shipping_id}
            )
        except Exception as exc:
            raise err_trash_shipping_address.with_internal(exc) from exc
        if row is None:
            raise err_shipping_address_not_found.with_internal(NoRowsError())
        return ShippingAddress.from_row(row)

    async def restore(self, shipping_id: int) -> ShippingAddress:
        try:
            row = await self._db.execute(
                _RESTORE_SHIPPING_ADDRESS, {"shipping_id": shipping_id}
            )
        except Exception as exc:
            raise err_restore_shipping_address.with_internal(exc) from exc
        if row is None:
            raise err_shipping_address_not_found.with_internal(NoRowsError())
        return ShippingAddress.from_row(row)

    async def delete_permanent(self, shipping_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_SHIPPING_ADDRESS_PERMANENTLY, {"shipping_id": shipping_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_shipping_address_permanent.with_internal(exc) from exc
        return True

    async def delete_by_order_id_permanent(self, order_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_SHIPPING_ADDRESS_BY_ORDER_PERMANENT, {"order_id": order_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_shipping_address_permanent.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_SHIPPING_ADDRESS)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_shipping_addresses.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_SHIPPING_ADDRESS)
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_all_permanent_shipping_address.with_internal(exc) from exc
        return True


__all__ = ["ShippingAddressCommandRepositoryImpl"]
