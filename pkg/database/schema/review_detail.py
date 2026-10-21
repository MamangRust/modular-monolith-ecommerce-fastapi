"""Row types for the review_details table. `caption` is nullable (stores it as `*string`), so the row dataclasses model it as `str | None`. Timestamps surface as `datetime.datetime`; the handlers format them as date-only strings (`%Y-%m-%d`) to match the `2006-01-02` layout."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ReviewDetail:

    review_detail_id: int
    review_id: int
    type: str
    url: str
    caption: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> ReviewDetail:
        return cls(
            review_detail_id=row["review_detail_id"],
            review_id=row["review_id"],
            type=row["type"],
            url=row["url"],
            caption=row.get("caption"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateReviewDetailRow:
    review_detail_id: int
    review_id: int
    type: str
    url: str
    caption: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateReviewDetailRow:
        return cls(
            review_detail_id=row["review_detail_id"],
            review_id=row["review_id"],
            type=row["type"],
            url=row["url"],
            caption=row.get("caption"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class GetReviewDetailByIDRow:
    """`FindById` projection — active rows only, no `deleted_at`."""

    review_detail_id: int
    review_id: int
    type: str
    url: str
    caption: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetReviewDetailByIDRow:
        return cls(
            review_detail_id=row["review_detail_id"],
            review_id=row["review_id"],
            type=row["type"],
            url=row["url"],
            caption=row.get("caption"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateReviewDetailRow = GetReviewDetailByIDRow


@dataclass
class GetReviewDetailsRow:
    """`FindAll` projection with a window total count (all rows, no deleted_at filter — matches review_detail `getReviewDetails`)."""

    review_detail_id: int
    review_id: int
    type: str
    url: str
    caption: str | None
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetReviewDetailsRow:
        return cls(
            review_detail_id=row["review_detail_id"],
            review_id=row["review_id"],
            type=row["type"],
            url=row["url"],
            caption=row.get("caption"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetReviewDetailsActiveRow:
    review_detail_id: int
    review_id: int
    type: str
    url: str
    caption: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetReviewDetailsActiveRow:
        return cls(
            review_detail_id=row["review_detail_id"],
            review_id=row["review_id"],
            type=row["type"],
            url=row["url"],
            caption=row.get("caption"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetReviewDetailsTrashedRow = GetReviewDetailsActiveRow


__all__ = [
    "CreateReviewDetailRow",
    "GetReviewDetailByIDRow",
    "GetReviewDetailsActiveRow",
    "GetReviewDetailsRow",
    "GetReviewDetailsTrashedRow",
    "ReviewDetail",
    "UpdateReviewDetailRow",
]
