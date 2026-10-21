"""Row <-> JSON helpers for the order item cache.

Order item rows carry `datetime` values that plain JSON cannot round-trip, so
the cache stores ISO-8601 strings and rebuilds the row dataclasses on read.
`total_count` is stored alongside the page rather than per row (the paginated
projections all carry it).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.order_item import (
    GetOrderItemsActiveRow,
    GetOrderItemsByOrderRow,
    GetOrderItemsRow,
)


def _iso_dt(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached order item payload")
    return datetime.fromisoformat(value)


def order_item_row_to_dict(
    row: GetOrderItemsRow | GetOrderItemsActiveRow,
) -> dict[str, Any]:
    return {
        "order_item_id": row.order_item_id,
        "order_id": row.order_id,
        "product_id": row.product_id,
        "quantity": row.quantity,
        "price": row.price,
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def order_item_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetOrderItemsRow:
    return GetOrderItemsRow(
        order_item_id=int(data["order_item_id"]),
        order_id=int(data["order_id"]),
        product_id=int(data["product_id"]),
        quantity=int(data["quantity"]),
        price=int(data["price"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        total_count=total_count,
    )


def active_row_to_dict(row: GetOrderItemsActiveRow) -> dict[str, Any]:
    payload = order_item_row_to_dict(row)
    payload["deleted_at"] = _iso_dt(row.deleted_at)
    return payload


def active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetOrderItemsActiveRow:
    return GetOrderItemsActiveRow(
        order_item_id=int(data["order_item_id"]),
        order_id=int(data["order_id"]),
        product_id=int(data["product_id"]),
        quantity=int(data["quantity"]),
        price=int(data["price"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt(data.get("deleted_at")),
        total_count=total_count,
    )


def by_order_row_to_dict(row: GetOrderItemsByOrderRow) -> dict[str, Any]:
    return {
        "order_item_id": row.order_item_id,
        "order_id": row.order_id,
        "product_id": row.product_id,
        "quantity": row.quantity,
        "price": row.price,
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def by_order_row_from_dict(data: dict[str, Any]) -> GetOrderItemsByOrderRow:
    return GetOrderItemsByOrderRow(
        order_item_id=int(data["order_item_id"]),
        order_id=int(data["order_id"]),
        product_id=int(data["product_id"]),
        quantity=int(data["quantity"]),
        price=int(data["price"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
    )


__all__ = [
    "active_row_from_dict",
    "active_row_to_dict",
    "by_order_row_from_dict",
    "by_order_row_to_dict",
    "order_item_row_from_dict",
    "order_item_row_to_dict",
]
