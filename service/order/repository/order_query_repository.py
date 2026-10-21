"""order read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page. the `$1::TEXT IS NULL OR...` search guards are dropped: binds a plain `string` (never nil) and an empty search already matches every row via `ILIKE '%%'` (same normalisation as the review repository). `find_by_id` maps a missing row to `err_order_not_found` (404) and any other failure to `err_find_by_id` (500)."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.order import (
    GetOrderByIDRow,
    GetOrdersActiveRow,
    GetOrdersByMerchantRow,
    GetOrdersRow,
    GetOrdersTrashedRow,
)
from shared.domain.requests.order import FindAllOrder, FindAllOrderByMerchant
from shared.errors.order_errors import (
    err_find_all_orders,
    err_find_by_active,
    err_find_by_id,
    err_find_by_merchant,
    err_find_by_trashed,
    err_order_not_found,
)

_GET_ORDERS = """
SELECT
    order_id,
    user_id,
    merchant_id,
    total_price,
    created_at,
    updated_at,
    COUNT(*) OVER () AS total_count
FROM orders
WHERE
    deleted_at IS NULL
    AND (
        order_id::TEXT ILIKE '%' || :search || '%'
        OR total_price::TEXT ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_ORDERS_ACTIVE = """
SELECT
    order_id,
    user_id,
    merchant_id,
    total_price,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM orders
WHERE
    deleted_at IS NULL
    AND (
        order_id::TEXT ILIKE '%' || :search || '%'
        OR total_price::TEXT ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_ORDERS_TRASHED = """
SELECT
    order_id,
    user_id,
    merchant_id,
    total_price,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM orders
WHERE
    deleted_at IS NOT NULL
    AND (
        order_id::TEXT ILIKE '%' || :search || '%'
        OR total_price::TEXT ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_ORDERS_BY_MERCHANT = """
SELECT
    order_id,
    user_id,
    merchant_id,
    total_price,
    created_at,
    updated_at,
    COUNT(*) OVER () AS total_count
FROM orders
WHERE
    deleted_at IS NULL
    AND (
        order_id::TEXT ILIKE '%' || :search || '%'
        OR total_price::TEXT ILIKE '%' || :search || '%'
    )
    AND merchant_id = :merchant_id
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_ORDER_BY_ID = """
SELECT
    order_id,
    user_id,
    merchant_id,
    total_price,
    created_at,
    updated_at
FROM orders
WHERE
    order_id = :order_id
    AND deleted_at IS NULL
"""


class OrderQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(self, request: FindAllOrder) -> list[GetOrdersRow]:
        params = {
            "search": request.search,
            "limit": request.page_size,
            "offset": (request.page - 1) * request.page_size,
        }
        try:
            rows = await self._db.select(_GET_ORDERS, params)
        except Exception as exc:
            raise err_find_all_orders.with_internal(exc) from exc
        return [GetOrdersRow.from_row(row) for row in rows]

    async def find_active(self, request: FindAllOrder) -> list[GetOrdersActiveRow]:
        params = {
            "search": request.search,
            "limit": request.page_size,
            "offset": (request.page - 1) * request.page_size,
        }
        try:
            rows = await self._db.select(_GET_ORDERS_ACTIVE, params)
        except Exception as exc:
            raise err_find_by_active.with_internal(exc) from exc
        return [GetOrdersActiveRow.from_row(row) for row in rows]

    async def find_trashed(self, request: FindAllOrder) -> list[GetOrdersTrashedRow]:
        params = {
            "search": request.search,
            "limit": request.page_size,
            "offset": (request.page - 1) * request.page_size,
        }
        try:
            rows = await self._db.select(_GET_ORDERS_TRASHED, params)
        except Exception as exc:
            raise err_find_by_trashed.with_internal(exc) from exc
        return [GetOrdersTrashedRow.from_row(row) for row in rows]

    async def find_by_merchant(
        self, request: FindAllOrderByMerchant
    ) -> list[GetOrdersByMerchantRow]:
        params = {
            "search": request.search,
            "merchant_id": request.merchant_id,
            "limit": request.page_size,
            "offset": (request.page - 1) * request.page_size,
        }
        try:
            rows = await self._db.select(_GET_ORDERS_BY_MERCHANT, params)
        except Exception as exc:
            raise err_find_by_merchant.with_internal(exc) from exc
        return [GetOrdersByMerchantRow.from_row(row) for row in rows]

    async def find_by_id(self, order_id: int) -> GetOrderByIDRow:
        try:
            row = await self._db.scalar(_GET_ORDER_BY_ID, {"order_id": order_id})
        except Exception as exc:
            raise err_find_by_id.with_internal(exc) from exc
        if row is None:
            raise err_order_not_found
        return GetOrderByIDRow.from_row(row)


__all__ = ["OrderQueryRepositoryImpl"]
