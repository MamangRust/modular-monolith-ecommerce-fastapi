"""Row -> proto mapping for the merchant_policy gRPC handlers. NORMALISATION: the mapper uses `time.Time.String` (`2006-01-02 15:04:05.999999999 -0700 MST`) for every timestamp and always attaches the `deleted_at` wrapper (a live row renders the zero time `0001-01-01 00:00:00 +0000 UTC`). uses the codebase-wide `.mmm` layout and only attaches the wrapper when the row is actually trashed, matching merchant_award/merchant_business. Unlike merchant_business, the merchant_policy mapping DOES copy `merchant_name` for the list rows (`GetMerchantPolicies*Row`); it is absent from the single/command rows. fills it whenever the row exposes it."""

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


def fill_merchant_policy_response(message: Any, row: Any) -> None:
    message.id = row.merchant_policy_id
    message.merchant_id = row.merchant_id
    message.policy_type = row.policy_type or ""
    message.title = row.title or ""
    message.description = row.description or ""
    message.created_at = format_timestamp_millis(row.created_at)
    message.updated_at = format_timestamp_millis(row.updated_at)
    merchant_name = getattr(row, "merchant_name", "")
    if merchant_name:
        message.merchant_name = merchant_name


def fill_merchant_policy_response_delete_at(message: Any, row: Any) -> None:
    fill_merchant_policy_response(message, row)
    deleted_at = format_timestamp_millis(getattr(row, "deleted_at", None))
    if deleted_at:
        message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=deleted_at))


__all__ = [
    "fill_merchant_policy_response",
    "fill_merchant_policy_response_delete_at",
    "normalize_page",
    "pagination_meta",
]
