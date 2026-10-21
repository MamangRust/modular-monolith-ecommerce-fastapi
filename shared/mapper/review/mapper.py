"""Review proto -> response DTO mapping. The proto already carries formatted strings, so this layer only shapes them into the REST envelopes. `deleted_at` presence differs per shape, matching: - `ReviewResponseDeleteAt` keeps `""` when the proto `StringValue` wrapper is present (the handler always sets it) and `None` when absent; - `ReviewsDetailResponse` keeps `None` unless the plain string is non-empty."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import PaginationMeta
from shared.domain.response.review import (
    ReviewDetailResponse,
    ReviewResponse,
    ReviewResponseDeleteAt,
    ReviewsDetailResponse,
)


def map_review_response(pb: Any) -> ReviewResponse:
    return ReviewResponse(
        id=int(pb.id),
        user_id=int(pb.user_id),
        product_id=int(pb.product_id),
        name=pb.name,
        comment=pb.comment,
        rating=int(pb.rating),
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_review_response_delete_at(pb: Any) -> ReviewResponseDeleteAt:
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else None
    return ReviewResponseDeleteAt(
        id=int(pb.id),
        user_id=int(pb.user_id),
        product_id=int(pb.product_id),
        name=pb.name,
        comment=pb.comment,
        rating=int(pb.rating),
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


def map_review_detail_response(pb: Any) -> ReviewDetailResponse:
    return ReviewDetailResponse(
        id=int(pb.id),
        type=pb.type,
        url=pb.url,
        caption=pb.caption,
        created_at=pb.created_at,
        updated_at="",  # never sets it (zero value)
    )


def map_reviews_detail_response(pb: Any) -> ReviewsDetailResponse:
    detail = (
        map_review_detail_response(pb.review_detail)
        if pb.HasField("review_detail")
        else None
    )
    return ReviewsDetailResponse(
        id=int(pb.id),
        user_id=int(pb.user_id),
        product_id=int(pb.product_id),
        name=pb.name,
        comment=pb.comment,
        rating=int(pb.rating),
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        review_detail=detail,
        deleted_at=pb.deleted_at or None,
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


__all__ = [
    "map_pagination_meta",
    "map_review_detail_response",
    "map_review_response",
    "map_review_response_delete_at",
    "map_reviews_detail_response",
]
