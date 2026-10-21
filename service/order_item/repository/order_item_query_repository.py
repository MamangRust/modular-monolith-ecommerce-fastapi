"""Order item read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip. Unlike category (`ORDER BY created_at DESC` everywhere), the trashed list orders by `deleted_at DESC`. the `WHERE ($1::TEXT IS NULL OR...)` first branch is dead: the handler always passes a non-null `search`, so an empty search matches everything through `ILIKE '%%'`. keeps only the effective predicate (same omission category documents)."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.order_item import (
    GetOrderItemsActiveRow,
    GetOrderItemsByOrderRow,
    GetOrderItemsRow,
    GetOrderItemsTrashedRow,
)

_GET_ORDER_ITEMS = """
SELECT
    order_item_id,
    order_id,
    product_id,
    quantity,
    price,
    created_at,
    updated_at,
    COUNT(*) OVER () AS total_count
FROM order_items
WHERE
    deleted_at IS NULL
    AND (
        order_id::TEXT ILIKE '%' || :search || '%'
        OR product_id::TEXT ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_ORDER_ITEMS_ACTIVE = """
SELECT
    order_item_id,
    order_id,
    product_id,
    quantity,
    price,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM order_items
WHERE
    deleted_at IS NULL
    AND (
        order_id::TEXT ILIKE '%' || :search || '%'
        OR product_id::TEXT ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_ORDER_ITEMS_TRASHED = """
SELECT
    order_item_id,
    order_id,
    product_id,
    quantity,
    price,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM order_items
WHERE
    deleted_at IS NOT NULL
    AND (
        order_id::TEXT ILIKE '%' || :search || '%'
        OR product_id::TEXT ILIKE '%' || :search || '%'
    )
ORDER BY deleted_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_ORDER_ITEMS_BY_ORDER = """
SELECT
    order_item_id,
    order_id,
    product_id,
    quantity,
    price,
    created_at,
    updated_at
FROM order_items
WHERE
    order_id = :order_id
    AND deleted_at IS NULL
"""


class OrderItemQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetOrderItemsRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_ORDER_ITEMS,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetOrderItemsRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetOrderItemsActiveRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_ORDER_ITEMS_ACTIVE,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetOrderItemsActiveRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetOrderItemsTrashedRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_ORDER_ITEMS_TRASHED,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetOrderItemsTrashedRow.from_row(row) for row in rows]

    async def find_order_item_by_order(
        self, order_id: int
    ) -> list[GetOrderItemsByOrderRow]:
        rows = await self._db.select(_GET_ORDER_ITEMS_BY_ORDER, {"order_id": order_id})
        return [GetOrderItemsByOrderRow.from_row(row) for row in rows]


__all__ = ["OrderItemQueryRepositoryImpl"]
