"""Review query-side REST mappers."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)
from shared.domain.response.review import (
    ReviewResponse,
    ReviewResponseDeleteAt,
    ReviewsDetailResponse,
)
from shared.mapper.review.mapper import (
    map_pagination_meta,
    map_review_response,
    map_review_response_delete_at,
    map_reviews_detail_response,
)


def to_api_response_review(pb: Any) -> ApiResponse[ReviewResponse]:
    return ApiResponse[ReviewResponse](
        status=pb.status,
        message=pb.message,
        data=map_review_response(pb.data),
    )


def to_api_responses_reviews(pb: Any) -> ApiResponse[list[ReviewResponse]]:
    return ApiResponse[list[ReviewResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_review_response(row) for row in pb.data],
    )


def to_api_response_pagination_review(
    pb: Any,
) -> APIResponsePagination[list[ReviewResponse]]:
    return APIResponsePagination[list[ReviewResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_review_response(row) for row in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_reviews_detail(
    pb: Any,
) -> APIResponsePagination[list[ReviewsDetailResponse]]:
    # drops the pagination block here (see module docstring): the struct's
    # `Pagination` field is left at its zero value, i.e. all four counters 0.
    return APIResponsePagination[list[ReviewsDetailResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_reviews_detail_response(row) for row in pb.data],
        pagination=PaginationMeta(
            current_page=0, page_size=0, total_pages=0, total_records=0
        ),
    )


def to_api_response_pagination_review_delete_at(
    pb: Any,
) -> APIResponsePagination[list[ReviewResponseDeleteAt]]:
    return APIResponsePagination[list[ReviewResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_review_response_delete_at(row) for row in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_pagination_review",
    "to_api_response_pagination_review_delete_at",
    "to_api_response_pagination_reviews_detail",
    "to_api_response_review",
    "to_api_responses_reviews",
]
