"""Row -> proto mapping for the product gRPC handlers. `mapToProtoProductResponse` type-switches over nine row shapes that all project the same base columns, plus the two stock rows (`UpdateProductCountStockRow`/`AdjustProductStockRow`) which carry only `product_id`/`count_in_stock`. A single attribute-driven filler reproduces every branch: absent attributes fall back to their zero value, so the stock rows emit only `id`/`count_in_stock`,. `deleted_at` follows the codebase convention (merchant_award/merchant_business): attached only when the row is actually trashed."""

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


def fill_product_response(message: Any, row: Any) -> None:
    message.id = getattr(row, "product_id", 0)
    message.merchant_id = getattr(row, "merchant_id", 0)
    message.category_id = getattr(row, "category_id", 0)
    message.name = getattr(row, "name", "") or ""
    message.description = getattr(row, "description", None) or ""
    message.price = getattr(row, "price", 0)
    message.count_in_stock = getattr(row, "count_in_stock", 0)
    message.brand = getattr(row, "brand", None) or ""
    message.weight = getattr(row, "weight", None) or 0
    message.rating = getattr(row, "rating", None) or 0.0
    message.slug_product = getattr(row, "slug_product", None) or ""
    message.image_product = getattr(row, "image_product", None) or ""
    message.created_at = format_timestamp_millis(getattr(row, "created_at", None))
    message.updated_at = format_timestamp_millis(getattr(row, "updated_at", None))


def fill_product_response_delete_at(message: Any, row: Any) -> None:
    fill_product_response(message, row)
    deleted_at = format_timestamp_millis(getattr(row, "deleted_at", None))
    if deleted_at:
        message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=deleted_at))


__all__ = [
    "fill_product_response",
    "fill_product_response_delete_at",
    "normalize_page",
    "pagination_meta",
]
