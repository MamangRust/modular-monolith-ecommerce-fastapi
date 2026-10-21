"""Order item write repository. Soft delete uses `deleted_at`; the permanent deletes are hard deletes. `create`/`update` return the raw driver error in (the service replaces it with its own sentinel); raises a wrapped AppError defensively, and the service still overrides it, so the wire result matches. `delete_order_item_by_order_permanent` purges every item of an order regardless of `deleted_at` (used by the order compensation path); `delete_all` additionally clears items whose parent order is trashed."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.order_item import (
    CreateOrderItemRow,
    OrderItem,
    UpdateOrderItemRow,
)
from shared.domain.requests.order_item import (
    CreateOrderItemRecordRequest,
    UpdateOrderItemRecordRequest,
)
from shared.errors import (
    AppError,
    err_calculate_total_price,
    err_create_order_item,
    err_delete_all_order_permanent,
    err_delete_order_item_permanent,
    err_order_item_not_found,
    err_restore_all_order_item,
    err_restore_order_item,
    err_trashed_order_item,
    err_update_order_item,
)

_CALCULATE_TOTAL_PRICE = """
SELECT COALESCE(SUM(quantity * price), 0)::int AS total_price
FROM order_items
WHERE
    order_id = :order_id
    AND deleted_at IS NULL
"""

_CREATE_ORDER_ITEM = """
INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES (:order_id, :product_id, :quantity, :price)
RETURNING
    order_item_id,
    order_id,
    product_id,
    quantity,
    price,
    created_at,
    updated_at
"""

_UPDATE_ORDER_ITEM = """
UPDATE order_items
SET
    quantity = :quantity,
    price = :price,
    updated_at = CURRENT_TIMESTAMP
WHERE
    order_item_id = :order_item_id
    AND deleted_at IS NULL
RETURNING
    order_item_id,
    order_id,
    product_id,
    quantity,
    price,
    created_at,
    updated_at
"""

_TRASH_ORDER_ITEM = """
UPDATE order_items
SET deleted_at = current_timestamp
WHERE
    order_item_id = :order_item_id
    AND deleted_at IS NULL
RETURNING
    order_item_id,
    order_id,
    product_id,
    quantity,
    price,
    created_at,
    updated_at,
    deleted_at
"""

_RESTORE_ORDER_ITEM = """
UPDATE order_items
SET deleted_at = NULL
WHERE
    order_item_id = :order_item_id
    AND deleted_at IS NOT NULL
RETURNING
    order_item_id,
    order_id,
    product_id,
    quantity,
    price,
    created_at,
    updated_at,
    deleted_at
"""

_DELETE_ORDER_ITEM_PERMANENTLY = """
DELETE FROM order_items
WHERE
    order_item_id = :order_item_id
    AND deleted_at IS NOT NULL
"""

_DELETE_ORDER_ITEMS_BY_ORDER_PERMANENT = (
    "DELETE FROM order_items WHERE order_id = :order_id"
)

_RESTORE_ALL_ORDER_ITEMS = (
    "UPDATE order_items SET deleted_at = NULL WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_PERMANENT_ORDER_ITEMS = """
DELETE FROM order_items
WHERE
    deleted_at IS NOT NULL
    OR order_id IN (SELECT order_id FROM orders WHERE deleted_at IS NOT NULL)
"""


class OrderItemCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(
        self, request: CreateOrderItemRecordRequest
    ) -> CreateOrderItemRow:
        params = {
            "order_id": request.order_id,
            "product_id": request.product_id,
            "quantity": request.quantity,
            "price": request.price,
        }
        try:
            row = await self._db.execute(_CREATE_ORDER_ITEM, params)
        except Exception as exc:
            raise err_create_order_item.with_internal(exc) from exc
        if row is None:
            raise err_create_order_item.with_internal(NoRowsError())
        return CreateOrderItemRow.from_row(row)

    async def update(
        self, request: UpdateOrderItemRecordRequest
    ) -> UpdateOrderItemRow:
        params = {
            "order_item_id": request.order_item_id,
            "quantity": request.quantity,
            "price": request.price,
        }
        try:
            row = await self._db.execute(_UPDATE_ORDER_ITEM, params)
        except Exception as exc:
            raise err_update_order_item.with_internal(exc) from exc
        if row is None:
            raise err_order_item_not_found.with_internal(NoRowsError())
        return UpdateOrderItemRow.from_row(row)

    async def trash(self, order_item_id: int) -> OrderItem:
        try:
            row = await self._db.execute(
                _TRASH_ORDER_ITEM, {"order_item_id": order_item_id}
            )
        except Exception as exc:
            raise err_trashed_order_item.with_internal(exc) from exc
        if row is None:
            raise err_order_item_not_found.with_internal(NoRowsError())
        return OrderItem.from_row(row)

    async def restore(self, order_item_id: int) -> OrderItem:
        try:
            row = await self._db.execute(
                _RESTORE_ORDER_ITEM, {"order_item_id": order_item_id}
            )
        except Exception as exc:
            raise err_restore_order_item.with_internal(exc) from exc
        if row is None:
            raise err_order_item_not_found.with_internal(NoRowsError())
        return OrderItem.from_row(row)

    async def delete_permanent(self, order_item_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_ORDER_ITEM_PERMANENTLY, {"order_item_id": order_item_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_order_item_permanent.with_internal(exc) from exc
        return True

    async def delete_order_item_by_order_permanent(self, order_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_ORDER_ITEMS_BY_ORDER_PERMANENT, {"order_id": order_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_order_item_permanent.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_ORDER_ITEMS)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_order_item.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_ORDER_ITEMS)
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_all_order_permanent.with_internal(exc) from exc
        return True

    async def calculate_total_price(self, order_id: int) -> int:
        try:
            row = await self._db.scalar(
                _CALCULATE_TOTAL_PRICE, {"order_id": order_id}
            )
        except Exception as exc:
            raise err_calculate_total_price.with_internal(exc) from exc
        # `Database.scalar` returns the first row mapping (sqlx `Get` semantics),
        # so the aggregate must be read by column name.
        return int(row["total_price"] or 0) if row is not None else 0


__all__ = ["OrderItemCommandRepositoryImpl"]
