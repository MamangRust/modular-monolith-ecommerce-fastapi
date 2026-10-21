"""Row -> proto mapping for the merchant_detail gRPC handlers. Timestamps are formatted `%Y-%m-%d %H:%M:%S.mmm` (`2006-01-02 15:04:05.000`), a new format for this domain — the existing `format_timestamp_millis` helper truncates Python's 6-digit `%f` to 3 digits. Nullable string columns collapse to `""` (`getString`). The proto `social_media_links` field is deliberately NOT filled: the mapping ignores the row's `SocialMediaLinks` column, so the wire response always carries an empty list. A NULL `deleted_at` attaches no wrapper, so the gateway renders `deleted_at: ""`."""

from __future__ import annotations

import math
from typing import Any

from google.protobuf import wrappers_pb2

from pb.common import api_pb2 as common_pb2
from shared.convert.convert import format_timestamp_millis


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


def fill_merchant_detail_response(message: Any, row: Any) -> None:
    message.id = row.merchant_detail_id
    message.merchant_id = row.merchant_id
    message.display_name = row.display_name or ""
    message.cover_image_url = row.cover_image_url or ""
    message.logo_url = row.logo_url or ""
    message.short_description = row.short_description or ""
    message.website_url = row.website_url or ""
    message.created_at = format_timestamp_millis(row.created_at)
    message.updated_at = format_timestamp_millis(row.updated_at)


def fill_merchant_detail_response_delete_at(message: Any, row: Any) -> None:
    fill_merchant_detail_response(message, row)
    deleted_at = format_timestamp_millis(row.deleted_at)
    if deleted_at:
        message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=deleted_at))


def fill_merchant_social_link_response(message: Any, row: Any) -> None:
    message.id = row.merchant_social_id
    message.merchant_detail_id = row.merchant_detail_id
    message.platform = row.platform
    message.url = row.url
    message.created_at = format_timestamp_millis(row.created_at)
    message.updated_at = format_timestamp_millis(row.updated_at)


__all__ = [
    "fill_merchant_detail_response",
    "fill_merchant_detail_response_delete_at",
    "fill_merchant_social_link_response",
    "normalize_page",
    "pagination_meta",
]
