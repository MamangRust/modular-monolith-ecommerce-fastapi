"""Row <-> JSON helpers for the cart cache.

`GetCartsRow` is all non-nullable columns plus the window `total_count`; the
timestamps are stored as ISO-8601 strings and `total_count` is stored alongside
the page rather than per row (see the query cache).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.cart import GetCartsRow


def _iso(value: datetime) -> str:
    return value.isoformat()


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached cart payload")
    return datetime.fromisoformat(value)


def cart_row_to_dict(row: GetCartsRow) -> dict[str, Any]:
    return {
        "cart_id": row.cart_id,
        "user_id": row.user_id,
        "product_id": row.product_id,
        "name": row.name,
        "price": row.price,
        "image": row.image,
        "quantity": row.quantity,
        "weight": row.weight,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def cart_row_from_dict(data: dict[str, Any], total_count: int) -> GetCartsRow:
    return GetCartsRow(
        cart_id=int(data["cart_id"]),
        user_id=int(data["user_id"]),
        product_id=int(data["product_id"]),
        name=data["name"],
        price=int(data["price"]),
        image=data["image"],
        quantity=int(data["quantity"]),
        weight=int(data["weight"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        total_count=total_count,
    )


def encode_page(rows: list[GetCartsRow], total: int) -> dict[str, Any]:
    return {"data": [cart_row_to_dict(row) for row in rows], "total_records": total}


def decode_page(payload: Any) -> tuple[list[GetCartsRow], int] | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    total = int(payload.get("total_records") or 0)
    return [cart_row_from_dict(item, total) for item in data], total


__all__ = [
    "cart_row_from_dict",
    "cart_row_to_dict",
    "decode_page",
    "encode_page",
]
