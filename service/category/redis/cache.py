"""Row <-> JSON helpers for the category cache.

Category rows carry `datetime` values that plain JSON cannot round-trip, so
the cache stores ISO-8601 strings and rebuilds the row dataclasses on read.
`total_count` is stored alongside the page rather than per row.

Stats rows are all `str`/`int`, so they round-trip through `dataclasses.asdict`
without conversion.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from pkg.database.schema.category import (
    GetCategoriesActiveRow,
    GetCategoriesRow,
    GetCategoryByIDRow,
)


def _iso_dt(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached category payload")
    return datetime.fromisoformat(value)


def _nullable(value: str | None) -> str | None:
    return value


def category_row_to_dict(
    row: GetCategoriesRow | GetCategoriesActiveRow,
) -> dict[str, Any]:
    return {
        "category_id": row.category_id,
        "name": row.name,
        "description": _nullable(row.description),
        "slug_category": _nullable(row.slug_category),
        "image_category": _nullable(row.image_category),
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def category_row_from_dict(data: dict[str, Any], total_count: int) -> GetCategoriesRow:
    return GetCategoriesRow(
        category_id=int(data["category_id"]),
        name=data["name"],
        description=data.get("description"),
        slug_category=data.get("slug_category"),
        image_category=data.get("image_category"),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        total_count=total_count,
    )


def active_row_to_dict(row: GetCategoriesActiveRow) -> dict[str, Any]:
    payload = category_row_to_dict(row)
    payload["deleted_at"] = _iso_dt(row.deleted_at)
    return payload


def active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetCategoriesActiveRow:
    return GetCategoriesActiveRow(
        category_id=int(data["category_id"]),
        name=data["name"],
        description=data.get("description"),
        slug_category=data.get("slug_category"),
        image_category=data.get("image_category"),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt(data.get("deleted_at")),
        total_count=total_count,
    )


def category_by_id_to_dict(row: GetCategoryByIDRow) -> dict[str, Any]:
    return {
        "category_id": row.category_id,
        "name": row.name,
        "description": _nullable(row.description),
        "slug_category": _nullable(row.slug_category),
        "image_category": _nullable(row.image_category),
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def category_by_id_from_dict(data: dict[str, Any]) -> GetCategoryByIDRow:
    return GetCategoryByIDRow(
        category_id=int(data["category_id"]),
        name=data["name"],
        description=data.get("description"),
        slug_category=data.get("slug_category"),
        image_category=data.get("image_category"),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
    )


# ---- stats payload helpers ----


def stats_rows_to_payload(rows: list[Any]) -> dict[str, Any]:
    return {"data": [asdict(row) for row in rows]}


def stats_rows_from_payload[T](cls: type[T], payload: Any) -> list[T] | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    return [cls(**item) for item in data]


__all__ = [
    "active_row_from_dict",
    "active_row_to_dict",
    "category_by_id_from_dict",
    "category_by_id_to_dict",
    "category_row_from_dict",
    "category_row_to_dict",
    "stats_rows_from_payload",
    "stats_rows_to_payload",
]
