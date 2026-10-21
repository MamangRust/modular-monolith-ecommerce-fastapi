"""Row -> proto mapping for the transaction gRPC handlers. Every transaction row shares the same base projection (`transaction_id`, `order_id`, `merchant_id`, `payment_method`, `amount`, `payment_status`, `created_at`, `updated_at`), so one `fill_transaction_response` handles all row types. Timestamps use the seconds layout `%Y-%m-%d %H:%M:%S` (`formatTimestamp`) — NO millis, unlike order/order_item. `deleted_at` is attached **only when non-empty** (`getStringValue` returns nil for an invalid timestamp, leaving the `StringValue` unset — the order/review_detail pattern, not the always-attach pattern)."""

from __future__ import annotations

import math
from typing import Any

from google.protobuf.wrappers_pb2 import StringValue

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


def fill_transaction_response(message: Any, row: Any) -> None:
    message.id = getattr(row, "transaction_id", 0)
    message.order_id = getattr(row, "order_id", 0)
    message.merchant_id = getattr(row, "merchant_id", 0)
    message.payment_method = getattr(row, "payment_method", "")
    message.amount = int(getattr(row, "amount", 0))
    message.payment_status = getattr(row, "payment_status", "")
    message.created_at = format_time_ptr(getattr(row, "created_at", None))
    message.updated_at = format_time_ptr(getattr(row, "updated_at", None))


def fill_transaction_response_delete_at(message: Any, row: Any) -> None:
    fill_transaction_response(message, row)
    deleted_at = format_time_ptr(getattr(row, "deleted_at", None))
    if deleted_at:
        message.deleted_at.CopyFrom(StringValue(value=deleted_at))


__all__ = [
    "fill_transaction_response",
    "fill_transaction_response_delete_at",
    "normalize_page",
    "pagination_meta",
]
