"""Row <-> JSON helpers for the review detail cache.

Review detail rows carry `datetime` values (and a nullable `caption`) that plain
JSON cannot round-trip, so the cache stores ISO-8601 strings (and `None`
captions) and rebuilds the row dataclasses on read. `total_count` is stored
alongside the page rather than per row.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.review_detail import (
    GetReviewDetailByIDRow,
    GetReviewDetailsActiveRow,
    GetReviewDetailsRow,
)


def _iso_dt(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached review detail payload")
    return datetime.fromisoformat(value)


def review_detail_row_to_dict(row: GetReviewDetailsRow | GetReviewDetailsActiveRow) -> dict[str, Any]:
    return {
        "review_detail_id": row.review_detail_id,
        "review_id": row.review_id,
        "type": row.type,
        "url": row.url,
        "caption": row.caption,
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def review_detail_row_from_dict(data: dict[str, Any], total_count: int) -> GetReviewDetailsRow:
    return GetReviewDetailsRow(
        review_detail_id=int(data["review_detail_id"]),
        review_id=int(data["review_id"]),
        type=data["type"],
        url=data["url"],
        caption=data.get("caption"),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        total_count=total_count,
    )


def active_row_to_dict(row: GetReviewDetailsActiveRow) -> dict[str, Any]:
    payload = review_detail_row_to_dict(row)
    payload["deleted_at"] = _iso_dt(row.deleted_at)
    return payload


def active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetReviewDetailsActiveRow:
    return GetReviewDetailsActiveRow(
        review_detail_id=int(data["review_detail_id"]),
        review_id=int(data["review_id"]),
        type=data["type"],
        url=data["url"],
        caption=data.get("caption"),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt(data.get("deleted_at")),
        total_count=total_count,
    )


def review_detail_by_id_to_dict(row: GetReviewDetailByIDRow) -> dict[str, Any]:
    return {
        "review_detail_id": row.review_detail_id,
        "review_id": row.review_id,
        "type": row.type,
        "url": row.url,
        "caption": row.caption,
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def review_detail_by_id_from_dict(data: dict[str, Any]) -> GetReviewDetailByIDRow:
    return GetReviewDetailByIDRow(
        review_detail_id=int(data["review_detail_id"]),
        review_id=int(data["review_id"]),
        type=data["type"],
        url=data["url"],
        caption=data.get("caption"),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
    )


def trashed_row_to_dict(row: GetReviewDetailsActiveRow) -> dict[str, Any]:
    payload = review_detail_row_to_dict(row)
    payload["deleted_at"] = _iso_dt(row.deleted_at)
    return payload


def trashed_row_from_dict(data: dict[str, Any], total_count: int) -> GetReviewDetailsActiveRow:
    return active_row_from_dict(data, total_count)


__all__ = [
    "active_row_from_dict",
    "active_row_to_dict",
    "review_detail_by_id_from_dict",
    "review_detail_by_id_to_dict",
    "review_detail_row_from_dict",
    "review_detail_row_to_dict",
    "trashed_row_from_dict",
    "trashed_row_to_dict",
]
