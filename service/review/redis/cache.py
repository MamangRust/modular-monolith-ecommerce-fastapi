"""Row <-> JSON helpers for the review cache.

Each row shape has its own encoder/decoder because the projections differ
(base + window total, base + `deleted_at` + total, base + `deleted_at` + total +
`review_details`, and the plain by-id base). Timestamps are stored as ISO-8601
strings; `total_count` is stored alongside the page rather than per row.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.review import (
    GetReviewByProductIdRow,
    GetReviewsActiveRow,
    GetReviewsRow,
    ReviewRow,
)


def _iso(value: datetime) -> str:
    return value.isoformat()


def _iso_opt(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt_required(value: Any) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached review payload")
    return datetime.fromisoformat(value)


def _dt_opt(value: Any) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


# ---- GetReviewsRow (FindAll) ----


def reviews_row_to_dict(row: GetReviewsRow) -> dict[str, Any]:
    return {
        "review_id": row.review_id,
        "user_id": row.user_id,
        "product_id": row.product_id,
        "name": row.name,
        "comment": row.comment,
        "rating": row.rating,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def reviews_row_from_dict(data: dict[str, Any], total: int) -> GetReviewsRow:
    return GetReviewsRow(
        review_id=int(data["review_id"]),
        user_id=int(data["user_id"]),
        product_id=int(data["product_id"]),
        name=data["name"],
        comment=data["comment"],
        rating=int(data["rating"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        total_count=total,
    )


# ---- GetReviewsActiveRow / GetReviewsTrashedRow ----


def reviews_active_row_to_dict(row: GetReviewsActiveRow) -> dict[str, Any]:
    payload = reviews_row_to_dict(
        GetReviewsRow(
            review_id=row.review_id,
            user_id=row.user_id,
            product_id=row.product_id,
            name=row.name,
            comment=row.comment,
            rating=row.rating,
            created_at=row.created_at,
            updated_at=row.updated_at,
            total_count=row.total_count,
        )
    )
    payload["deleted_at"] = _iso_opt(row.deleted_at)
    return payload


def reviews_active_row_from_dict(data: dict[str, Any], total: int) -> GetReviewsActiveRow:
    return GetReviewsActiveRow(
        review_id=int(data["review_id"]),
        user_id=int(data["user_id"]),
        product_id=int(data["product_id"]),
        name=data["name"],
        comment=data["comment"],
        rating=int(data["rating"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt_opt(data.get("deleted_at")),
        total_count=total,
    )


# ---- GetReviewByProductIdRow / GetReviewByMerchantIdRow ----


def review_detail_row_to_dict(row: GetReviewByProductIdRow) -> dict[str, Any]:
    return {
        "review_id": row.review_id,
        "user_id": row.user_id,
        "product_id": row.product_id,
        "name": row.name,
        "comment": row.comment,
        "rating": row.rating,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
        "deleted_at": _iso_opt(row.deleted_at),
        "review_details": row.review_details,
    }


def review_detail_row_from_dict(data: dict[str, Any], total: int) -> GetReviewByProductIdRow:
    details = data.get("review_details")
    return GetReviewByProductIdRow(
        review_id=int(data["review_id"]),
        user_id=int(data["user_id"]),
        product_id=int(data["product_id"]),
        name=data["name"],
        comment=data["comment"],
        rating=int(data["rating"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt_opt(data.get("deleted_at")),
        total_count=total,
        review_details=details if isinstance(details, list) else None,
    )


# ---- ReviewRow (by id) ----


def review_by_id_to_dict(row: ReviewRow) -> dict[str, Any]:
    return {
        "review_id": row.review_id,
        "user_id": row.user_id,
        "product_id": row.product_id,
        "name": row.name,
        "comment": row.comment,
        "rating": row.rating,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def review_by_id_from_dict(data: Any) -> ReviewRow | None:
    if not isinstance(data, dict):
        return None
    return ReviewRow(
        review_id=int(data["review_id"]),
        user_id=int(data["user_id"]),
        product_id=int(data["product_id"]),
        name=data["name"],
        comment=data["comment"],
        rating=int(data["rating"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
    )


__all__ = [
    "review_by_id_from_dict",
    "review_by_id_to_dict",
    "review_detail_row_from_dict",
    "review_detail_row_to_dict",
    "reviews_active_row_from_dict",
    "reviews_active_row_to_dict",
    "reviews_row_from_dict",
    "reviews_row_to_dict",
]
