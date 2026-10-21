"""Row -> proto mapping for the merchant gRPC handlers. Timestamps are formatted `%Y-%m-%d %H:%M:%S` (`2006-01-02 15:04:05`), a new format for this domain. Nullable string columns collapse to `""` (`getString`). The document `uploaded_at` is filled from the row `created_at`, matching (`formatTimestamp(v.CreatedAt)`); the DB `uploaded_at` column never reaches the wire. A NULL `deleted_at` attaches no wrapper, so the gateway renders `deleted_at: null`."""

from __future__ import annotations

import math
from typing import Any

from google.protobuf import wrappers_pb2

from pb.common import api_pb2 as common_pb2
from shared.convert.convert import format_time_ptr


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


def fill_merchant_response(message: Any, row: Any) -> None:
    message.id = row.merchant_id
    message.user_id = row.user_id
    message.name = row.name
    message.description = row.description or ""
    message.address = row.address or ""
    message.contact_email = row.contact_email or ""
    message.contact_phone = row.contact_phone or ""
    message.status = row.status
    message.created_at = format_time_ptr(row.created_at)
    message.updated_at = format_time_ptr(row.updated_at)


def fill_merchant_response_delete_at(message: Any, row: Any) -> None:
    fill_merchant_response(message, row)
    deleted_at = format_time_ptr(row.deleted_at)
    if deleted_at:
        message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=deleted_at))


def fill_merchant_document(message: Any, row: Any) -> None:
    message.document_id = row.document_id
    message.merchant_id = row.merchant_id
    message.document_type = row.document_type
    message.document_url = row.document_url
    message.status = row.status
    message.note = row.note or ""
    # fills proto `uploaded_at` from the row `created_at`.
    message.uploaded_at = format_time_ptr(row.created_at)
    message.updated_at = format_time_ptr(row.updated_at)


def fill_merchant_document_delete_at(message: Any, row: Any) -> None:
    fill_merchant_document(message, row)
    deleted_at = format_time_ptr(row.deleted_at)
    if deleted_at:
        message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=deleted_at))


__all__ = [
    "fill_merchant_document",
    "fill_merchant_document_delete_at",
    "fill_merchant_response",
    "fill_merchant_response_delete_at",
    "normalize_page",
    "pagination_meta",
]
