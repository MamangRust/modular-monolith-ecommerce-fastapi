"""Review detail response DTOs. Both the proto field (`ReviewDetailsResponse.id`) and the REST field are `id`, so the mapper reads `pb.id` directly with no translation. Date/timestamp strings are already formatted by the gRPC handlers (date-only `%Y-%m-%d` to match the `2006-01-02` layout), so the mapper passes them through unchanged. `caption` may be `None` (NULL in the DB)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class ReviewDetailResponse:
    id: int
    review_id: int
    type: str
    url: str
    caption: str | None
    created_at: str
    updated_at: str


@dataclass
class ReviewDetailResponseDeleteAt:
    id: int
    review_id: int
    type: str
    url: str
    caption: str | None
    created_at: str
    updated_at: str
    deleted_at: str | None = None


# API response wrappers (kept close to the names) ----

ReviewDetailResponseAll = ApiResponse[None]
ReviewDetailResponseDelete = ApiResponse[None]
ReviewDetailResponseApi = ApiResponse[ReviewDetailResponse]
ReviewDetailResponseDeleteAtApi = ApiResponse[ReviewDetailResponseDeleteAt]
ReviewDetailsResponse = ApiResponse[list[ReviewDetailResponse]]
ReviewDetailResponsePagination = APIResponsePagination[list[ReviewDetailResponse]]
ReviewDetailResponsePaginationDeleteAt = APIResponsePagination[
    list[ReviewDetailResponseDeleteAt]
]


def pagination_meta(page: int, page_size: int, total_records: int) -> PaginationMeta:
    total_pages = math.ceil(total_records / page_size) if page_size else 0
    return PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total_records,
    )


__all__ = [
    "ReviewDetailResponse",
    "ReviewDetailResponseAll",
    "ReviewDetailResponseApi",
    "ReviewDetailResponseDelete",
    "ReviewDetailResponseDeleteAt",
    "ReviewDetailResponseDeleteAtApi",
    "ReviewDetailResponsePagination",
    "ReviewDetailResponsePaginationDeleteAt",
    "ReviewDetailsResponse",
    "pagination_meta",
]
