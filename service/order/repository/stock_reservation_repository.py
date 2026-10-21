"""stock reservation ledger repository. methods return the raw pgx error. The `:one` methods surface a missing `RETURNING` row as `NoRowsError` (the `pgx.ErrNoRows` equivalent), which the command service checks to drive its conditional-transition compensation logic."""

from __future__ import annotations

from datetime import datetime

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.order import OrderStockReservation

_GET_BY_ORDER = """
SELECT reservation_id, order_id, product_id, quantity, status, created_at, updated_at
FROM order_stock_reservations
WHERE order_id = :order_id
ORDER BY product_id
"""

_GET_RESERVED_FOR_TRASHED_ORDERS = """
SELECT r.reservation_id, r.order_id, r.product_id, r.quantity, r.status, r.created_at, r.updated_at
FROM order_stock_reservations r
JOIN orders o ON o.order_id = r.order_id
WHERE o.deleted_at IS NOT NULL AND r.status = 'reserved'
ORDER BY r.order_id, r.product_id
"""

_GET_RELEASED_FOR_TRASHED_ORDERS = """
SELECT r.reservation_id, r.order_id, r.product_id, r.quantity, r.status, r.created_at, r.updated_at
FROM order_stock_reservations r
JOIN orders o ON o.order_id = r.order_id
WHERE o.deleted_at IS NOT NULL AND r.status = 'released'
ORDER BY r.order_id, r.product_id
"""

_GET_RELEASED_FOR_ACTIVE_ORDERS = """
SELECT r.reservation_id, r.order_id, r.product_id, r.quantity, r.status, r.created_at, r.updated_at
FROM order_stock_reservations r
JOIN orders o ON o.order_id = r.order_id
WHERE o.deleted_at IS NULL AND r.status = 'released'
ORDER BY r.order_id, r.product_id
"""

_UPSERT = """
INSERT INTO order_stock_reservations (order_id, product_id, quantity, status)
VALUES (:order_id, :product_id, :quantity, 'reserved')
ON CONFLICT (order_id, product_id)
DO UPDATE SET
    quantity = order_stock_reservations.quantity + EXCLUDED.quantity,
    status = 'reserved',
    updated_at = CURRENT_TIMESTAMP
RETURNING reservation_id, order_id, product_id, quantity, status, created_at, updated_at
"""

_UPDATE_QUANTITY = """
UPDATE order_stock_reservations
SET quantity = :quantity, status = 'reserved', updated_at = CURRENT_TIMESTAMP
WHERE order_id = :order_id AND product_id = :product_id
RETURNING reservation_id, order_id, product_id, quantity, status, created_at, updated_at
"""

_RELEASE = """
UPDATE order_stock_reservations
SET status = 'released', updated_at = CURRENT_TIMESTAMP
WHERE order_id = :order_id AND product_id = :product_id AND status = 'reserved'
RETURNING reservation_id, order_id, product_id, quantity, status, created_at, updated_at
"""

_RESERVE = """
UPDATE order_stock_reservations
SET status = 'reserved', updated_at = CURRENT_TIMESTAMP
WHERE order_id = :order_id AND product_id = :product_id AND status = 'released'
RETURNING reservation_id, order_id, product_id, quantity, status, created_at, updated_at
"""

_DELETE_BY_ORDER_PRODUCT = """
DELETE FROM order_stock_reservations
WHERE order_id = :order_id AND product_id = :product_id
"""

_DELETE_BY_ORDER = """
DELETE FROM order_stock_reservations WHERE order_id = :order_id
"""

_DELETE_ALL_FOR_TRASHED_ORDERS = """
DELETE FROM order_stock_reservations
WHERE order_id IN (SELECT order_id FROM orders WHERE deleted_at IS NOT NULL)
"""

_DELETE_OLD_RELEASED_RESERVATIONS = """
DELETE FROM order_stock_reservations r
USING orders o
WHERE r.order_id = o.order_id
  AND r.status = 'released'
  AND o.deleted_at IS NOT NULL
  AND r.updated_at < :cutoff
RETURNING r.reservation_id
"""

_DELETE_OLD_PRODUCT_STOCK_ADJUSTMENTS = """
DELETE FROM product_stock_adjustments
WHERE created_at < :cutoff
RETURNING operation_id
"""


class StockReservationRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get_by_order(self, order_id: int) -> list[OrderStockReservation]:
        rows = await self._db.select(_GET_BY_ORDER, {"order_id": order_id})
        return [OrderStockReservation.from_row(row) for row in rows]

    async def upsert(
        self, order_id: int, product_id: int, quantity: int
    ) -> OrderStockReservation:
        row = await self._db.execute(
            _UPSERT,
            {
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
            },
        )
        if row is None:
            raise NoRowsError()
        return OrderStockReservation.from_row(row)

    async def update_quantity(
        self, order_id: int, product_id: int, quantity: int
    ) -> OrderStockReservation:
        row = await self._db.execute(
            _UPDATE_QUANTITY,
            {
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
            },
        )
        if row is None:
            raise NoRowsError()
        return OrderStockReservation.from_row(row)

    async def release(
        self, order_id: int, product_id: int
    ) -> OrderStockReservation:
        row = await self._db.execute(
            _RELEASE, {"order_id": order_id, "product_id": product_id}
        )
        if row is None:
            raise NoRowsError()
        return OrderStockReservation.from_row(row)

    async def reserve(
        self, order_id: int, product_id: int
    ) -> OrderStockReservation:
        row = await self._db.execute(
            _RESERVE, {"order_id": order_id, "product_id": product_id}
        )
        if row is None:
            raise NoRowsError()
        return OrderStockReservation.from_row(row)

    async def get_reserved_for_trashed_orders(
        self,
    ) -> list[OrderStockReservation]:
        rows = await self._db.select(_GET_RESERVED_FOR_TRASHED_ORDERS)
        return [OrderStockReservation.from_row(row) for row in rows]

    async def get_released_for_trashed_orders(
        self,
    ) -> list[OrderStockReservation]:
        rows = await self._db.select(_GET_RELEASED_FOR_TRASHED_ORDERS)
        return [OrderStockReservation.from_row(row) for row in rows]

    async def delete_by_order(self, order_id: int) -> None:
        await self._db.execute(_DELETE_BY_ORDER, {"order_id": order_id})

    async def delete_by_order_product(
        self, order_id: int, product_id: int
    ) -> None:
        await self._db.execute(
            _DELETE_BY_ORDER_PRODUCT,
            {"order_id": order_id, "product_id": product_id},
        )

    async def delete_all_for_trashed_orders(self) -> None:
        await self._db.execute(_DELETE_ALL_FOR_TRASHED_ORDERS)

    async def get_released_for_active_orders(
        self,
    ) -> list[OrderStockReservation]:
        rows = await self._db.select(_GET_RELEASED_FOR_ACTIVE_ORDERS)
        return [OrderStockReservation.from_row(row) for row in rows]

    async def delete_old_released_reservations(self, cutoff: datetime) -> int:
        rows = await self._db.execute_all(
            _DELETE_OLD_RELEASED_RESERVATIONS, {"cutoff": cutoff}
        )
        return len(rows)

    async def delete_old_product_stock_adjustments(
        self, cutoff: datetime
    ) -> int:
        rows = await self._db.execute_all(
            _DELETE_OLD_PRODUCT_STOCK_ADJUSTMENTS, {"cutoff": cutoff}
        )
        return len(rows)


__all__ = ["StockReservationRepositoryImpl"]
