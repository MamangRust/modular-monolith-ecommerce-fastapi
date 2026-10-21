"""Review detail row/proto -> response DTO mapping. Two input shapes, one output: - row dataclasses — format the timestamp values as date-only strings (`%Y-%m-%d`) to match the `2006-01-02` layout; a NULL `caption` becomes `None` on the row mapper; - proto messages — already-formatted date-only strings, passed through unchanged; `caption` is coerced from `None` to `""` because the proto field is always present."""

from __future__ import annotations

from typing import Any

from pkg.database.schema.review_detail import (
    CreateReviewDetailRow,
    GetReviewDetailByIDRow,
    GetReviewDetailsActiveRow,
    GetReviewDetailsRow,
    ReviewDetail,
    UpdateReviewDetailRow,
)
from shared.convert.convert import format_date
from shared.domain.response.responses import (
    PaginationMeta,
)
from shared.domain.response.review_detail import (
    ReviewDetailResponse,
    ReviewDetailResponseAll,
    ReviewDetailResponseApi,
    ReviewDetailResponseDelete,
    ReviewDetailResponseDeleteAt,
    ReviewDetailResponseDeleteAtApi,
    ReviewDetailResponsePagination,
    ReviewDetailResponsePaginationDeleteAt,
)

ReviewDetailRow = (
    ReviewDetail
    | CreateReviewDetailRow
    | GetReviewDetailByIDRow
    | GetReviewDetailsRow
    | UpdateReviewDetailRow
)
ReviewDetailDeleteAtRow = ReviewDetail | GetReviewDetailsActiveRow


def to_review_detail_response(row: ReviewDetailRow) -> ReviewDetailResponse:
    return ReviewDetailResponse(
        id=row.review_detail_id,
        review_id=row.review_id,
        type=row.type,
        url=row.url,
        caption=row.caption,
        created_at=format_date(row.created_at),
        updated_at=format_date(row.updated_at),
    )


def to_review_detail_response_delete_at(
    row: ReviewDetailDeleteAtRow,
) -> ReviewDetailResponseDeleteAt:
    return ReviewDetailResponseDeleteAt(
        id=row.review_detail_id,
        review_id=row.review_id,
        type=row.type,
        url=row.url,
        caption=row.caption,
        created_at=format_date(row.created_at),
        updated_at=format_date(row.updated_at),
        deleted_at=format_date(row.deleted_at) or None,
    )


def map_review_detail_response(pb: Any) -> ReviewDetailResponse:
    return ReviewDetailResponse(
        id=int(pb.id),
        review_id=int(pb.review_id),
        type=pb.type,
        url=pb.url,
        caption=pb.caption or None,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_review_detail_response_delete_at(pb: Any) -> ReviewDetailResponseDeleteAt:
    # always sets the pointer, so an absent wrapper renders as "".
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return ReviewDetailResponseDeleteAt(
        id=int(pb.id),
        review_id=int(pb.review_id),
        type=pb.type,
        url=pb.url,
        caption=pb.caption or None,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at or None,
    )


def map_pagination_meta(meta: Any) -> PaginationMeta:
    if meta is None:
        return PaginationMeta()
    return PaginationMeta(
        current_page=int(meta.current_page),
        page_size=int(meta.page_size),
        total_pages=int(meta.total_pages),
        total_records=int(meta.total_records),
    )


# ---- REST envelopes (proto -> ApiResponse) ----


def to_api_response_review_detail(pb: Any) -> ReviewDetailResponseApi:
    return ReviewDetailResponseApi(
        status=pb.status,
        message=pb.message,
        data=map_review_detail_response(pb.data),
    )


def to_api_response_review_detail_delete_at(pb: Any) -> ReviewDetailResponseDeleteAtApi:
    return ReviewDetailResponseDeleteAtApi(
        status=pb.status,
        message=pb.message,
        data=map_review_detail_response_delete_at(pb.data),
    )


def to_api_response_pagination_review_detail(pb: Any) -> ReviewDetailResponsePagination:
    return ReviewDetailResponsePagination(
        status=pb.status,
        message=pb.message,
        data=[map_review_detail_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_review_detail_delete_at(
    pb: Any,
) -> ReviewDetailResponsePaginationDeleteAt:
    return ReviewDetailResponsePaginationDeleteAt(
        status=pb.status,
        message=pb.message,
        data=[map_review_detail_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_review_detail_delete(pb: Any) -> ReviewDetailResponseDelete:
    # `DeleteReviewDetailPermanent` returns `pb.review.ApiResponseReviewDelete`.
    return ReviewDetailResponseDelete(status=pb.status, message=pb.message)


def to_api_response_review_detail_all(pb: Any) -> ReviewDetailResponseAll:
    # Bulk `RestoreAll` / `DeleteAll` return `pb.review.ApiResponseReviewAll`.
    return ReviewDetailResponseAll(status=pb.status, message=pb.message)


__all__ = [
    "map_pagination_meta",
    "map_review_detail_response",
    "map_review_detail_response_delete_at",
    "to_api_response_pagination_review_detail",
    "to_api_response_pagination_review_detail_delete_at",
    "to_api_response_review_detail",
    "to_api_response_review_detail_all",
    "to_api_response_review_detail_delete",
    "to_api_response_review_detail_delete_at",
    "to_review_detail_response",
    "to_review_detail_response_delete_at",
]
