"""Row <-> JSON helpers for the product caches.

Product rows mix plain `str`/`int` columns with nullable `str`/`int`/`float`
(`description`, `brand`, `weight`, `rating`, `slug_product`, `image_product`)
and `datetime` timestamps. Nullable fields are stored as-is; timestamps are
stored as ISO-8601 strings. `total_count` is stored alongside the page rather
than per row (see the query cache).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.product import (
    GetProductByIDRow,
    GetProductsActiveRow,
    GetProductsByMerchantRow,
    GetProductsRow,
)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached product payload")
    return datetime.fromisoformat(value)


def _base_fields(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "product_id": int(data["product_id"]),
        "merchant_id": int(data["merchant_id"]),
        "category_id": int(data["category_id"]),
        "name": data["name"],
        "description": data.get("description"),
        "price": int(data["price"]),
        "count_in_stock": int(data["count_in_stock"]),
        "brand": data.get("brand"),
        "weight": data.get("weight"),
        "rating": data.get("rating"),
        "slug_product": data.get("slug_product"),
        "image_product": data.get("image_product"),
        "created_at": _dt_required(data.get("created_at")),
        "updated_at": _dt_required(data.get("updated_at")),
    }


def _base_to_dict(row: Any) -> dict[str, Any]:
    return {
        "product_id": row.product_id,
        "merchant_id": row.merchant_id,
        "category_id": row.category_id,
        "name": row.name,
        "description": row.description,
        "price": row.price,
        "count_in_stock": row.count_in_stock,
        "brand": row.brand,
        "weight": row.weight,
        "rating": row.rating,
        "slug_product": row.slug_product,
        "image_product": row.image_product,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


# ---- list rows (FindAll) ----


def product_row_to_dict(row: GetProductsRow) -> dict[str, Any]:
    return _base_to_dict(row)


def product_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetProductsRow:
    return GetProductsRow(**_base_fields(data), total_count=total_count)


# ---- active/trashed rows (carry deleted_at) ----


def product_active_row_to_dict(row: GetProductsActiveRow) -> dict[str, Any]:
    return {**_base_to_dict(row), "deleted_at": _iso(row.deleted_at)}


def product_active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetProductsActiveRow:
    return GetProductsActiveRow(
        **_base_fields(data),
        deleted_at=_dt(data.get("deleted_at")),
        total_count=total_count,
    )


# ---- merchant/category rows (carry category_name) ----


def product_merchant_row_to_dict(row: GetProductsByMerchantRow) -> dict[str, Any]:
    return {**_base_to_dict(row), "category_name": row.category_name}


def product_merchant_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetProductsByMerchantRow:
    return GetProductsByMerchantRow(
        **_base_fields(data),
        category_name=data["category_name"],
        total_count=total_count,
    )


# ---- single row (FindById) ----


def product_by_id_to_dict(row: GetProductByIDRow) -> dict[str, Any]:
    return _base_to_dict(row)


def product_by_id_from_dict(data: dict[str, Any]) -> GetProductByIDRow:
    return GetProductByIDRow(**_base_fields(data))


# ---- page envelopes (shared by the query caches) ----


def encode_page(rows: list, total: int, to_dict) -> dict[str, Any]:
    return {"data": [to_dict(row) for row in rows], "total_records": total}


def decode_page(payload: Any, from_dict) -> tuple[list, int] | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    total = int(payload.get("total_records") or 0)
    return [from_dict(item, total) for item in data], total


__all__ = [
    "decode_page",
    "encode_page",
    "product_active_row_from_dict",
    "product_active_row_to_dict",
    "product_by_id_from_dict",
    "product_by_id_to_dict",
    "product_merchant_row_from_dict",
    "product_merchant_row_to_dict",
    "product_row_from_dict",
    "product_row_to_dict",
]
