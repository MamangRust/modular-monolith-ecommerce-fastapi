"""Row -> proto mapping for the review gRPC handlers. The plain review rows (`GetReviewsRow`/`GetReviewsActiveRow`/`GetReviewsTrashedRow`/ `GetReviewByIDRow`/`CreateReviewRow`/`UpdateReviewRow`) format their timestamps date-only (`%Y-%m-%d`); the detail rows (`GetReviewByProductIdRow`/ `GetReviewByMerchantIdRow`) use `%Y-%m-%d %H:%M:%S.mmm`.: always attaches the `deleted_at` StringValue wrapper for the `ReviewResponseDeleteAt` shape — even when the row is active (empty value). reproduces that (unlike product/merchant_award, which only attach it when non-empty), so the REST mapper sees `HasField("deleted_at") == True` and emits `""` for active rows. The nested `ReviewDetailResponse` is built from the *first* aggregated `review_details` element; its `created_at` is passed through as-is (never re-formats it) and `updated_at` is left at its zero value (never sets it)."""

from __future__ import annotations

import math
from typing import Any

from google.protobuf import wrappers_pb2

from pb.common import api_pb2 as common_pb2
from shared.convert.convert import format_date, format_timestamp_millis


def normalize_page(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def pagination_meta(page: int, page_size: int, total: int) -> Any:
    total_pages = math.ceil(total / page_size) if page_size else 0
    return common_pb2.PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total,
    )


def fill_review_response(message: Any, row: Any) -> None:
    message.id = getattr(row, "review_id", 0)
    message.user_id = getattr(row, "user_id", 0)
    message.product_id = getattr(row, "product_id", 0)
    message.name = getattr(row, "name", "") or ""
    message.comment = getattr(row, "comment", "") or ""
    message.rating = getattr(row, "rating", 0)
    message.created_at = format_date(getattr(row, "created_at", None))
    message.updated_at = format_date(getattr(row, "updated_at", None))


def fill_review_response_delete_at(message: Any, row: Any) -> None:
    fill_review_response(message, row)
    # always sets the wrapper (empty value when the row is not trashed).
    message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=format_date(getattr(row, "deleted_at", None))))


def fill_review_detail_response(message: Any, detail: dict[str, Any]) -> None:
    message.id = detail.get("detail_id", 0) or 0
    message.type = detail.get("type", "") or ""
    message.url = detail.get("url", "") or ""
    message.caption = detail.get("caption", "") or ""
    message.created_at = detail.get("created_at", "") or ""


def fill_reviews_detail_response(message: Any, row: Any) -> None:
    message.id = getattr(row, "review_id", 0)
    message.user_id = getattr(row, "user_id", 0)
    message.product_id = getattr(row, "product_id", 0)
    message.name = getattr(row, "name", "") or ""
    message.comment = getattr(row, "comment", "") or ""
    message.rating = getattr(row, "rating", 0)
    message.created_at = format_timestamp_millis(getattr(row, "created_at", None))
    message.updated_at = format_timestamp_millis(getattr(row, "updated_at", None))
    deleted_at = format_timestamp_millis(getattr(row, "deleted_at", None))
    if deleted_at:
        message.deleted_at = deleted_at
    details = getattr(row, "review_details", None)
    if details:
        fill_review_detail_response(message.review_detail, details[0])


__all__ = [
    "fill_review_detail_response",
    "fill_review_response",
    "fill_review_response_delete_at",
    "fill_reviews_detail_response",
    "normalize_page",
    "pagination_meta",
]
