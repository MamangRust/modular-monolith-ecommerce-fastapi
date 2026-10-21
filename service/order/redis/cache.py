"""Row <-> JSON helpers for the order cache.

Each projection has its own encoder/decoder because the column sets differ
(base + window total, base + `deleted_at` + total, plain by-id base, and the four
stats shapes). Timestamps are stored as ISO-8601 strings; `total_count` is stored
alongside the page rather than per row.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.order import (
    GetMonthlyOrderRow,
    GetMonthlyTotalRevenueRow,
    GetOrdersActiveRow,
    GetOrdersRow,
    GetOrdersTrashedRow,
    GetYearlyOrderRow,
    GetYearlyTotalRevenueRow,
    OrderRow,
)


def _iso(value: datetime) -> str:
    return value.isoformat()


def _iso_opt(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt_required(value: Any) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached order payload")
    return datetime.fromisoformat(value)


def _dt_opt(value: Any) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


# ---- GetOrdersRow (FindAll / FindByMerchant) ----


def orders_row_to_dict(row: GetOrdersRow) -> dict[str, Any]:
    return {
        "order_id": row.order_id,
        "user_id": row.user_id,
        "merchant_id": row.merchant_id,
        "total_price": row.total_price,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def orders_row_from_dict(data: dict[str, Any], total: int) -> GetOrdersRow:
    return GetOrdersRow(
        order_id=int(data["order_id"]),
        user_id=int(data["user_id"]),
        merchant_id=int(data["merchant_id"]),
        total_price=int(data["total_price"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        total_count=total,
    )


# ---- GetOrdersActiveRow / GetOrdersTrashedRow ----


def orders_active_row_to_dict(row: GetOrdersActiveRow) -> dict[str, Any]:
    return {
        "order_id": row.order_id,
        "user_id": row.user_id,
        "merchant_id": row.merchant_id,
        "total_price": row.total_price,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
        "deleted_at": _iso_opt(row.deleted_at),
    }


def orders_active_row_from_dict(
    data: dict[str, Any], total: int
) -> GetOrdersActiveRow:
    return GetOrdersActiveRow(
        order_id=int(data["order_id"]),
        user_id=int(data["user_id"]),
        merchant_id=int(data["merchant_id"]),
        total_price=int(data["total_price"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt_opt(data.get("deleted_at")),
        total_count=total,
    )


def orders_trashed_row_to_dict(row: GetOrdersTrashedRow) -> dict[str, Any]:
    return {
        "order_id": row.order_id,
        "user_id": row.user_id,
        "merchant_id": row.merchant_id,
        "total_price": row.total_price,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
        "deleted_at": _iso_opt(row.deleted_at),
    }


def orders_trashed_row_from_dict(
    data: dict[str, Any], total: int
) -> GetOrdersTrashedRow:
    return GetOrdersTrashedRow(
        order_id=int(data["order_id"]),
        user_id=int(data["user_id"]),
        merchant_id=int(data["merchant_id"]),
        total_price=int(data["total_price"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt_opt(data.get("deleted_at")),
        total_count=total,
    )


# ---- OrderRow (FindByID) ----


def order_by_id_to_dict(row: OrderRow) -> dict[str, Any]:
    return {
        "order_id": row.order_id,
        "user_id": row.user_id,
        "merchant_id": row.merchant_id,
        "total_price": row.total_price,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def order_by_id_from_dict(data: Any) -> OrderRow | None:
    if not isinstance(data, dict):
        return None
    return OrderRow(
        order_id=int(data["order_id"]),
        user_id=int(data["user_id"]),
        merchant_id=int(data["merchant_id"]),
        total_price=int(data["total_price"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
    )


# ---- stats rows ----


def monthly_total_revenue_row_to_dict(row: GetMonthlyTotalRevenueRow) -> dict[str, Any]:
    return {
        "year": row.year,
        "month": row.month,
        "total_revenue": row.total_revenue,
    }


def monthly_total_revenue_row_from_dict(data: dict[str, Any]) -> GetMonthlyTotalRevenueRow:
    return GetMonthlyTotalRevenueRow(
        year=data["year"],
        month=data["month"],
        total_revenue=int(data["total_revenue"]),
    )


def yearly_total_revenue_row_to_dict(row: GetYearlyTotalRevenueRow) -> dict[str, Any]:
    return {"year": row.year, "total_revenue": row.total_revenue}


def yearly_total_revenue_row_from_dict(data: dict[str, Any]) -> GetYearlyTotalRevenueRow:
    return GetYearlyTotalRevenueRow(
        year=data["year"], total_revenue=int(data["total_revenue"])
    )


def monthly_order_row_to_dict(row: GetMonthlyOrderRow) -> dict[str, Any]:
    return {
        "month": row.month,
        "order_count": row.order_count,
        "total_revenue": row.total_revenue,
        "total_items_sold": row.total_items_sold,
    }


def monthly_order_row_from_dict(data: dict[str, Any]) -> GetMonthlyOrderRow:
    return GetMonthlyOrderRow(
        month=data["month"],
        order_count=int(data["order_count"]),
        total_revenue=float(data["total_revenue"]),
        total_items_sold=int(data["total_items_sold"]),
    )


def yearly_order_row_to_dict(row: GetYearlyOrderRow) -> dict[str, Any]:
    return {
        "year": row.year,
        "order_count": row.order_count,
        "total_revenue": row.total_revenue,
        "total_items_sold": row.total_items_sold,
        "unique_products_sold": row.unique_products_sold,
    }


def yearly_order_row_from_dict(data: dict[str, Any]) -> GetYearlyOrderRow:
    return GetYearlyOrderRow(
        year=data["year"],
        order_count=int(data["order_count"]),
        total_revenue=float(data["total_revenue"]),
        total_items_sold=int(data["total_items_sold"]),
        unique_products_sold=int(data["unique_products_sold"]),
    )


__all__ = [
    "monthly_order_row_from_dict",
    "monthly_order_row_to_dict",
    "monthly_total_revenue_row_from_dict",
    "monthly_total_revenue_row_to_dict",
    "order_by_id_from_dict",
    "order_by_id_to_dict",
    "orders_active_row_from_dict",
    "orders_active_row_to_dict",
    "orders_row_from_dict",
    "orders_row_to_dict",
    "orders_trashed_row_from_dict",
    "orders_trashed_row_to_dict",
    "yearly_order_row_from_dict",
    "yearly_order_row_to_dict",
    "yearly_total_revenue_row_from_dict",
    "yearly_total_revenue_row_to_dict",
]
