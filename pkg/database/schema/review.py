"""Row types for the reviews table. `review_details` is the `json_agg` of the review's attachments (see the SQL). asyncpg decodes the `json`/`jsonb` aggregate into a Python list of dicts; a raw string is tolerated too (defensive `_parse_details`). `comment` is `TEXT NOT NULL`; `deleted_at` is nullable. Timestamps surface as `datetime.datetime`; the handlers format them (`%Y-%m-%d` for the plain review rows, `%Y-%m-%d %H:%M:%S.mmm` for the detail rows — matching two layouts)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


def _parse_details(value: Any) -> list[dict[str, Any]] | None:
    """Normalise the `review_details` aggregate into a list of dicts."""
    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return None
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return None


@dataclass
class Review:

    review_id: int
    user_id: int
    product_id: int
    name: str
    comment: str
    rating: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> Review:
        return cls(
            review_id=row["review_id"],
            user_id=row["user_id"],
            product_id=row["product_id"],
            name=row["name"],
            comment=row["comment"],
            rating=row["rating"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class ReviewRow:
    """Base projection: GetReviewByID/Create/Update RETURNING columns."""

    review_id: int
    user_id: int
    product_id: int
    name: str
    comment: str
    rating: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> ReviewRow:
        return cls(
            review_id=row["review_id"],
            user_id=row["user_id"],
            product_id=row["product_id"],
            name=row["name"],
            comment=row["comment"],
            rating=row["rating"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# declares a distinct struct per query even though the fields are identical.
GetReviewByIDRow = ReviewRow
CreateReviewRow = ReviewRow
UpdateReviewRow = ReviewRow


@dataclass
class GetReviewsRow:
    """`GetReviews` (FindAll) projection with window total count."""

    review_id: int
    user_id: int
    product_id: int
    name: str
    comment: str
    rating: int
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetReviewsRow:
        return cls(
            review_id=row["review_id"],
            user_id=row["user_id"],
            product_id=row["product_id"],
            name=row["name"],
            comment=row["comment"],
            rating=row["rating"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetReviewsActiveRow:
    """`GetReviewsActive`/`...Trashed`: base + `deleted_at` + total."""

    review_id: int
    user_id: int
    product_id: int
    name: str
    comment: str
    rating: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetReviewsActiveRow:
        return cls(
            review_id=row["review_id"],
            user_id=row["user_id"],
            product_id=row["product_id"],
            name=row["name"],
            comment=row["comment"],
            rating=row["rating"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetReviewsTrashedRow = GetReviewsActiveRow


@dataclass
class GetReviewByProductIdRow:
    """`GetReviewByProductId`/`...ByMerchantId`: base + `deleted_at` + total + the aggregated `review_details` JSON array."""

    review_id: int
    user_id: int
    product_id: int
    name: str
    comment: str
    rating: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int
    review_details: list[dict[str, Any]] | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetReviewByProductIdRow:
        return cls(
            review_id=row["review_id"],
            user_id=row["user_id"],
            product_id=row["product_id"],
            name=row["name"],
            comment=row["comment"],
            rating=row["rating"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
            review_details=_parse_details(row.get("review_details")),
        )


GetReviewByMerchantIdRow = GetReviewByProductIdRow


__all__ = [
    "CreateReviewRow",
    "GetReviewByIDRow",
    "GetReviewByMerchantIdRow",
    "GetReviewByProductIdRow",
    "GetReviewsActiveRow",
    "GetReviewsRow",
    "GetReviewsTrashedRow",
    "Review",
    "ReviewRow",
    "UpdateReviewRow",
]
