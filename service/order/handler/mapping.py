"""Row -> proto mapping for the order gRPC handlers. Every order row shares the same base projection (`order_id`, `merchant_id`, `user_id`, `total_price`, `created_at`, `updated_at`), so one `fill_order_response` handles all row types. Timestamps use the millisecond layout `%Y-%m-%d %H:%M:%S.mmm` (`formatTimestamp`). `deleted_at` is attached **only when non-empty** (unlike review, which always attaches the wrapper): `mapToProtoOrderResponseDeleteAt` guards on `formatTimestamp(deletedAt) != ""`, so an active row leaves the `StringValue` unset. The REST `OrderResponseDeleteAt` mapper then emits `""` for the absent field."""

from __future__ import annotations

import math
from typing import Any

from google.protobuf.wrappers_pb2 import StringValue

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


def fill_order_response(message: Any, row: Any) -> None:
    message.id = getattr(row, "order_id", 0)
    message.merchant_id = getattr(row, "merchant_id", 0)
    message.user_id = getattr(row, "user_id", 0)
    message.total_price = int(getattr(row, "total_price", 0))
    message.created_at = format_timestamp_millis(getattr(row, "created_at", None))
    message.updated_at = format_timestamp_millis(getattr(row, "updated_at", None))


def fill_order_response_delete_at(message: Any, row: Any) -> None:
    fill_order_response(message, row)
    deleted_at = format_timestamp_millis(getattr(row, "deleted_at", None))
    if deleted_at:
        message.deleted_at.CopyFrom(StringValue(value=deleted_at))


__all__ = [
    "fill_order_response",
    "fill_order_response_delete_at",
    "normalize_page",
    "pagination_meta",
]
