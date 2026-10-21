"""Review response DTOs. Field names match the REST DTOs. Date strings are already formatted by the gRPC handlers, so the mappers pass them through unchanged. Timestamp layouts differ per shape (matching): - `ReviewResponse`/`ReviewResponseDeleteAt` -> `%Y-%m-%d` (date only); - `ReviewsDetailResponse` (and its nested detail) -> `%Y-%m-%d %H:%M:%S.mmm`. `deleted_at` is a nullable string: - on `ReviewResponseDeleteAt` the mapper sets it whenever the proto wrapper is present (the handler always sets it, so it is `""` for active rows); - on `ReviewsDetailResponse` it is `None` unless non-empty. The two `ApiResponseReviewDelete`/`ApiResponseReviewAll` envelopes (status + message only) are shared with the `review_detail` domain, whose `DeleteReviewDetailPermanent` / bulk ops reuse the same `pb.review` messages."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class ReviewResponse:
    id: int
    user_id: int
    product_id: int
    name: str
    comment: str
    rating: int
    created_at: str
    updated_at: str


@dataclass
class ReviewResponseDeleteAt:
    id: int
    user_id: int
    product_id: int
    name: str
    comment: str
    rating: int
    created_at: str
    updated_at: str
    deleted_at: str | None = None


@dataclass
class ReviewDetailResponse:
    """Nested attachment on `ReviewsDetailResponse` (json-tag typo noted)."""

    id: int
    type: str
    url: str
    caption: str
    created_at: str
    updated_at: str = ""


@dataclass
class ReviewsDetailResponse:
    id: int
    user_id: int
    product_id: int
    name: str
    comment: str
    rating: int
    created_at: str
    updated_at: str
    review_detail: ReviewDetailResponse | None = field(default=None)
    deleted_at: str | None = None


# ---- status/message-only envelopes (shared with review_detail) ----


@dataclass
class ApiResponseReviewDelete:
    status: str
    message: str


@dataclass
class ApiResponseReviewAll:
    status: str
    message: str


# API response wrappers (kept close to the names) ----

ReviewResponseApi = ApiResponse[ReviewResponse]
ReviewResponseDeleteAtApi = ApiResponse[ReviewResponseDeleteAt]
ReviewResponses = ApiResponse[list[ReviewResponse]]
ReviewResponseDelete = ApiResponse[None]
ReviewResponseAll = ApiResponse[None]
ReviewResponsePagination = APIResponsePagination[list[ReviewResponse]]
ReviewResponsePaginationDeleteAt = APIResponsePagination[list[ReviewResponseDeleteAt]]
ReviewResponsePaginationDetail = APIResponsePagination[list[ReviewsDetailResponse]]

# Aliases used by the review_detail domain.
ReviewDeleteResponse = ApiResponse[None]
ReviewAllResponse = ApiResponse[None]


def to_api_response_review_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_review_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def pagination_meta(page: int, page_size: int, total_records: int) -> PaginationMeta:
    total_pages = math.ceil(total_records / page_size) if page_size else 0
    return PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total_records,
    )


__all__ = [
    "ApiResponseReviewAll",
    "ApiResponseReviewDelete",
    "ReviewAllResponse",
    "ReviewDeleteResponse",
    "ReviewDetailResponse",
    "ReviewResponse",
    "ReviewResponseAll",
    "ReviewResponseApi",
    "ReviewResponseDelete",
    "ReviewResponseDeleteAt",
    "ReviewResponseDeleteAtApi",
    "ReviewResponsePagination",
    "ReviewResponsePaginationDeleteAt",
    "ReviewResponsePaginationDetail",
    "ReviewResponses",
    "ReviewsDetailResponse",
    "pagination_meta",
    "to_api_response_review_all",
    "to_api_response_review_delete",
]
