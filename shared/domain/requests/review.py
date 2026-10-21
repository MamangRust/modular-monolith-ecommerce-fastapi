"""Review request DTOs. Validation Matches the expected `validator` tags: - `CreateReviewRequest` has NO validator tags at all, so `Validate` always passes (zero values are accepted) — keeps defaults on every field so a missing JSON member becomes a zero value, exactly like Echo's; - `UpdateReviewRequest` requires `rating` (`required` -> non-zero) and `comment` (`required` -> non-empty); `review_id`/`name` are unvalidated. `FindAllReviews`/`FindAllReviewsByProduct`/`FindAllReviewsByMerchant` and `CreateReviewRecord` are internal records (structs), not user input, so they stay plain dataclasses; only the two command DTOs are pydantic-validated (and only in the gRPC handler / gateway body, matching). NOTE: `CreateReviewRequest` carries no `name`; the repository `CreateReviewParams.Name` is therefore always `""`. `CreateReviewRecord` keeps the `name` field (it SQL params) but the service leaves it empty."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, field_validator


@dataclass
class FindAllReviews:
    """Service/cache request (`requests.FindAllReview`)."""

    search: str
    page: int
    page_size: int


@dataclass
class FindAllReviewsByProduct:
    """Service/cache request (`requests.FindAllReviewByProduct`)."""

    product_id: int
    rating: int
    search: str
    page: int
    page_size: int


@dataclass
class FindAllReviewsByMerchant:
    """Service/cache request (`requests.FindAllReviewByMerchant`)."""

    merchant_id: int
    rating: int
    search: str
    page: int
    page_size: int


@dataclass
class CreateReviewRecord:
    """Repository create params (`db.CreateReviewParams`). `name` is part of the SQL params but never populates it from the request, so the service passes `""`."""

    user_id: int
    product_id: int
    name: str
    comment: str
    rating: int


class CreateReviewRequest(BaseModel):
    """`requests.CreateReviewRequest` — no validator constraints."""

    user_id: int = 0
    product_id: int = 0
    rating: int = 0
    comment: str = ""


class UpdateReviewRequest(BaseModel):
    """`requests.UpdateReviewRequest` — `rating`/`comment` required."""

    review_id: int | None = None
    name: str = ""
    rating: int = 0
    comment: str = ""

    @field_validator("rating")
    @classmethod
    def _rating_required(cls, value: int) -> int:
        if value == 0:
            raise ValueError("rating is required")
        return value

    @field_validator("comment")
    @classmethod
    def _comment_required(cls, value: str) -> str:
        if not value:
            raise ValueError("comment is required")
        return value


__all__ = [
    "CreateReviewRecord",
    "CreateReviewRequest",
    "FindAllReviews",
    "FindAllReviewsByMerchant",
    "FindAllReviewsByProduct",
    "UpdateReviewRequest",
]
