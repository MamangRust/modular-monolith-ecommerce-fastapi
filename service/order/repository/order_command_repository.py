"""order write repository. `create`/`update`/`trash`/`restore`/`find_trashed_by_id` map a missing `RETURNING` row to `err_order_not_found` (wraps `pgx.ErrNoRows`). `delete_permanent_with_children` is `:one`: the atomic data-modifying CTE purges the trashed order's stock reservations, order items, transactions and shipping addresses together with the order. A non-trashed order yields no `RETURNING` row, surfaced as `err_order_not_found`."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.order import Order, OrderRow
from shared.domain.requests.order import (
    CreateOrderRecordRequest,
    UpdateOrderRecordRequest,
)
from shared.errors.order_errors import (
    err_create_order,
    err_delete_all_order_permanent,
    err_delete_order_permanent,
    err_find_by_id,
    err_find_by_trashed,
    err_order_not_found,
    err_restore_all_order,
    err_restore_order,
    err_trashed_order,
    err_update_order,
)

_CREATE_ORDER = """
INSERT INTO orders (
    merchant_id,
    user_id,
    total_price
)
VALUES (
    :merchant_id,
    :user_id,
    :total_price
)
RETURNING
    order_id,
    user_id,
    merchant_id,
    total_price,
    created_at,
    updated_at
"""

_UPDATE_ORDER = """
UPDATE orders
SET
    total_price = :total_price,
    updated_at = CURRENT_TIMESTAMP
WHERE
    order_id = :order_id
    AND deleted_at IS NULL
RETURNING
    order_id,
    user_id,
    merchant_id,
    total_price,
    created_at,
    updated_at
"""

_TRASH_ORDER = """
UPDATE orders
SET
    deleted_at = CURRENT_TIMESTAMP
WHERE
    order_id = :order_id
    AND deleted_at IS NULL
RETURNING
    order_id,
    user_id,
    merchant_id,
    total_price,
    created_at,
    updated_at,
    deleted_at
"""

_RESTORE_ORDER = """
UPDATE orders
SET
    deleted_at = NULL
WHERE
    order_id = :order_id
    AND deleted_at IS NOT NULL
RETURNING
    order_id,
    user_id,
    merchant_id,
    total_price,
    created_at,
    updated_at,
    deleted_at
"""

_GET_TRASHED_ORDER = """
SELECT
    order_id,
    user_id,
    merchant_id,
    total_price,
    created_at,
    updated_at,
    deleted_at
FROM orders
WHERE order_id = :order_id AND deleted_at IS NOT NULL
"""

_GET_TRASHED_ORDERS = """
SELECT
    order_id,
    user_id,
    merchant_id,
    total_price,
    created_at,
    updated_at,
    deleted_at
FROM orders
WHERE deleted_at IS NOT NULL
ORDER BY order_id
"""

_DELETE_ORDER_PERMANENTLY = """
DELETE FROM orders WHERE order_id = :order_id AND deleted_at IS NOT NULL
"""

_DELETE_ORDER_PERMANENTLY_WITH_CHILDREN = """
WITH
    trashed AS (
        SELECT order_id FROM orders
        WHERE order_id = :order_id AND deleted_at IS NOT NULL
    ),
    deleted_reservations AS (
        DELETE FROM order_stock_reservations
        WHERE order_id IN (SELECT order_id FROM trashed)
    ),
    deleted_items AS (
        DELETE FROM order_items
        WHERE order_id IN (SELECT order_id FROM trashed)
    ),
    deleted_transactions AS (
        DELETE FROM transactions
        WHERE order_id IN (SELECT order_id FROM trashed)
    ),
    deleted_addresses AS (
        DELETE FROM shipping_addresses
        WHERE order_id IN (SELECT order_id FROM trashed)
    )
DELETE FROM orders o
WHERE o.order_id = :order_id AND o.deleted_at IS NOT NULL
RETURNING o.order_id
"""

_RESTORE_ALL_ORDERS = """
UPDATE orders SET deleted_at = NULL WHERE deleted_at IS NOT NULL
"""

_DELETE_ALL_PERMANENT_ORDERS = """
DELETE FROM orders WHERE deleted_at IS NOT NULL
"""


class OrderCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(self, request: CreateOrderRecordRequest) -> OrderRow:
        params = {
            "merchant_id": request.merchant_id,
            "user_id": request.user_id,
            "total_price": request.total_price,
        }
        try:
            row = await self._db.execute(_CREATE_ORDER, params)
        except Exception as exc:
            raise err_create_order.with_internal(exc) from exc
        if row is None:
            raise err_order_not_found
        return OrderRow.from_row(row)

    async def update(self, request: UpdateOrderRecordRequest) -> OrderRow:
        params = {
            "order_id": request.order_id,
            "total_price": request.total_price,
        }
        try:
            row = await self._db.execute(_UPDATE_ORDER, params)
        except Exception as exc:
            raise err_update_order.with_internal(exc) from exc
        if row is None:
            raise err_order_not_found
        return OrderRow.from_row(row)

    async def trash(self, order_id: int) -> Order:
        try:
            row = await self._db.execute(_TRASH_ORDER, {"order_id": order_id})
        except Exception as exc:
            raise err_trashed_order.with_internal(exc) from exc
        if row is None:
            raise err_order_not_found
        return Order.from_row(row)

    async def restore(self, order_id: int) -> Order:
        try:
            row = await self._db.execute(_RESTORE_ORDER, {"order_id": order_id})
        except Exception as exc:
            raise err_restore_order.with_internal(exc) from exc
        if row is None:
            raise err_order_not_found
        return Order.from_row(row)

    async def delete_permanent(self, order_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_ORDER_PERMANENTLY, {"order_id": order_id}
            )
        except Exception as exc:
            raise err_delete_order_permanent.with_internal(exc) from exc
        return True

    async def delete_permanent_with_children(self, order_id: int) -> bool:
        try:
            row = await self._db.execute(
                _DELETE_ORDER_PERMANENTLY_WITH_CHILDREN, {"order_id": order_id}
            )
        except Exception as exc:
            raise err_delete_order_permanent.with_internal(exc) from exc
        if row is None:
            raise err_order_not_found
        return True

    async def find_trashed_by_id(self, order_id: int) -> Order:
        try:
            row = await self._db.scalar(
                _GET_TRASHED_ORDER, {"order_id": order_id}
            )
        except Exception as exc:
            raise err_find_by_id.with_internal(exc) from exc
        if row is None:
            raise err_order_not_found
        return Order.from_row(row)

    async def find_trashed(self) -> list[Order]:
        try:
            rows = await self._db.select(_GET_TRASHED_ORDERS)
        except Exception as exc:
            raise err_find_by_trashed.with_internal(exc) from exc
        return [Order.from_row(row) for row in rows]

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_ORDERS)
        except Exception as exc:
            raise err_restore_all_order.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_ORDERS)
        except Exception as exc:
            raise err_delete_all_order_permanent.with_internal(exc) from exc
        return True


__all__ = ["OrderCommandRepositoryImpl"]
