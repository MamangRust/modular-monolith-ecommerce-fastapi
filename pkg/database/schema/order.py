"""Row types for the `orders` / `order_stock_reservations` tables. Stats rows keep the SQL column types exactly (note `total_revenue` is `float64` on the order-summary rows but `int32` on the total-revenue rows; the handler truncates to `int32` for the proto, matching `int32(...)` casts). Order timestamps are formatted `%Y-%m-%d %H:%M:%S.mmm` (with millis) by the handler, unlike cart/review's date-only rows."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Order:

    order_id: int
    user_id: int
    merchant_id: int
    total_price: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> Order:
        return cls(
            order_id=row["order_id"],
            user_id=row["user_id"],
            merchant_id=row["merchant_id"],
            total_price=row["total_price"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class OrderRow:
    """Base projection (`CreateOrder` / `UpdateOrder` / `GetOrderByID`)."""

    order_id: int
    user_id: int
    merchant_id: int
    total_price: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> OrderRow:
        return cls(
            order_id=row["order_id"],
            user_id=row["user_id"],
            merchant_id=row["merchant_id"],
            total_price=row["total_price"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# declares distinct names with identical fields.
CreateOrderRow = OrderRow
UpdateOrderRow = OrderRow
GetOrderByIDRow = OrderRow


@dataclass
class GetOrdersRow:
    """`GetOrders` (FindAll) projection with the window total count."""

    order_id: int
    user_id: int
    merchant_id: int
    total_price: int
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetOrdersRow:
        return cls(
            order_id=row["order_id"],
            user_id=row["user_id"],
            merchant_id=row["merchant_id"],
            total_price=row["total_price"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


# `GetOrdersByMerchant` has the same projection as `GetOrders`.
GetOrdersByMerchantRow = GetOrdersRow


@dataclass
class GetOrdersActiveRow:
    """`GetOrdersActive` projection (adds `deleted_at` + `total_count`)."""

    order_id: int
    user_id: int
    merchant_id: int
    total_price: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetOrdersActiveRow:
        return cls(
            order_id=row["order_id"],
            user_id=row["user_id"],
            merchant_id=row["merchant_id"],
            total_price=row["total_price"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


@dataclass
class GetOrdersTrashedRow:
    """`GetOrdersTrashed` projection (adds `deleted_at` + `total_count`)."""

    order_id: int
    user_id: int
    merchant_id: int
    total_price: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetOrdersTrashedRow:
        return cls(
            order_id=row["order_id"],
            user_id=row["user_id"],
            merchant_id=row["merchant_id"],
            total_price=row["total_price"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


@dataclass
class OrderStockReservation:

    reservation_id: int
    order_id: int
    product_id: int
    quantity: int
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> OrderStockReservation:
        return cls(
            reservation_id=row["reservation_id"],
            order_id=row["order_id"],
            product_id=row["product_id"],
            quantity=row["quantity"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# ---- stats rows ----


@dataclass
class GetMonthlyTotalRevenueRow:
    year: str
    month: str
    total_revenue: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMonthlyTotalRevenueRow:
        return cls(
            year=row["year"],
            month=row["month"],
            total_revenue=int(row["total_revenue"]),
        )


@dataclass
class GetYearlyTotalRevenueRow:
    year: str
    total_revenue: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetYearlyTotalRevenueRow:
        return cls(year=row["year"], total_revenue=int(row["total_revenue"]))


@dataclass
class GetMonthlyOrderRow:
    month: str
    order_count: int
    total_revenue: float
    total_items_sold: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMonthlyOrderRow:
        return cls(
            month=row["month"],
            order_count=int(row["order_count"]),
            total_revenue=float(row["total_revenue"]),
            total_items_sold=int(row["total_items_sold"]),
        )


@dataclass
class GetYearlyOrderRow:
    year: str
    order_count: int
    total_revenue: float
    total_items_sold: int
    unique_products_sold: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetYearlyOrderRow:
        return cls(
            year=row["year"],
            order_count=int(row["order_count"]),
            total_revenue=float(row["total_revenue"]),
            total_items_sold=int(row["total_items_sold"]),
            unique_products_sold=int(row["unique_products_sold"]),
        )


# by-merchant variants have identical shapes.
GetMonthlyTotalRevenueByMerchantRow = GetMonthlyTotalRevenueRow
GetYearlyTotalRevenueByMerchantRow = GetYearlyTotalRevenueRow
GetMonthlyOrderByMerchantRow = GetMonthlyOrderRow
GetYearlyOrderByMerchantRow = GetYearlyOrderRow


__all__ = [
    "CreateOrderRow",
    "GetMonthlyOrderByMerchantRow",
    "GetMonthlyOrderRow",
    "GetMonthlyTotalRevenueByMerchantRow",
    "GetMonthlyTotalRevenueRow",
    "GetOrderByIDRow",
    "GetOrdersActiveRow",
    "GetOrdersByMerchantRow",
    "GetOrdersRow",
    "GetOrdersTrashedRow",
    "GetYearlyOrderByMerchantRow",
    "GetYearlyOrderRow",
    "GetYearlyTotalRevenueByMerchantRow",
    "GetYearlyTotalRevenueRow",
    "Order",
    "OrderRow",
    "OrderStockReservation",
    "UpdateOrderRow",
]
