"""Row <-> JSON helpers for the slider cache.

Slider rows carry `datetime` values that plain JSON cannot round-trip, so the
cache stores ISO-8601 strings and rebuilds the row dataclasses on read.
`total_count` is stored alongside the page rather than per row.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.slider import (
    GetSliderByIDRow,
    GetSlidersActiveRow,
    GetSlidersRow,
)


def _iso_dt(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached slider payload")
    return datetime.fromisoformat(value)


def slider_row_to_dict(row: GetSlidersRow | GetSlidersActiveRow) -> dict[str, Any]:
    return {
        "slider_id": row.slider_id,
        "name": row.name,
        "image": row.image,
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def slider_row_from_dict(data: dict[str, Any], total_count: int) -> GetSlidersRow:
    return GetSlidersRow(
        slider_id=int(data["slider_id"]),
        name=data["name"],
        image=data["image"],
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        total_count=total_count,
    )


def active_row_to_dict(row: GetSlidersActiveRow) -> dict[str, Any]:
    payload = slider_row_to_dict(row)
    payload["deleted_at"] = _iso_dt(row.deleted_at)
    return payload


def active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetSlidersActiveRow:
    return GetSlidersActiveRow(
        slider_id=int(data["slider_id"]),
        name=data["name"],
        image=data["image"],
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt(data.get("deleted_at")),
        total_count=total_count,
    )


def slider_by_id_to_dict(row: GetSliderByIDRow) -> dict[str, Any]:
    return {
        "slider_id": row.slider_id,
        "name": row.name,
        "image": row.image,
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def slider_by_id_from_dict(data: dict[str, Any]) -> GetSliderByIDRow:
    return GetSliderByIDRow(
        slider_id=int(data["slider_id"]),
        name=data["name"],
        image=data["image"],
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
    )


__all__ = [
    "active_row_from_dict",
    "active_row_to_dict",
    "slider_by_id_from_dict",
    "slider_by_id_to_dict",
    "slider_row_from_dict",
    "slider_row_to_dict",
]
