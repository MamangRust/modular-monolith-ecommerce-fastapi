"""Row -> proto mapping for the merchant_business gRPC handlers. All timestamps use `%Y-%m-%d %H:%M:%S.mmm` (`2006-01-02 15:04:05.000` layout) — the table has no `DATE` columns, so there is no date-only branch here. Nullable strings collapse to `""` and nullable ints to `0` (`getString` / `getInt32`). `merchant_name` is deliberately NOT filled: the mapping never reads the row's `MerchantName`, so the proto (and REST) always carries `""`. A NULL `deleted_at` attaches no wrapper, so the gateway renders `deleted_at: ""`."""

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


def fill_merchant_business_response(message: Any, row: Any) -> None:
    message.id = row.merchant_business_info_id
    message.merchant_id = row.merchant_id
    message.business_type = row.business_type or ""
    message.tax_id = row.tax_id or ""
    message.established_year = row.established_year or 0
    message.number_of_employees = row.number_of_employees or 0
    message.website_url = row.website_url or ""
    message.created_at = format_timestamp_millis(row.created_at)
    message.updated_at = format_timestamp_millis(row.updated_at)


def fill_merchant_business_response_delete_at(message: Any, row: Any) -> None:
    fill_merchant_business_response(message, row)
    deleted_at = format_timestamp_millis(row.deleted_at)
    if deleted_at:
        message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=deleted_at))


__all__ = [
    "fill_merchant_business_response",
    "fill_merchant_business_response_delete_at",
    "normalize_page",
    "pagination_meta",
]
