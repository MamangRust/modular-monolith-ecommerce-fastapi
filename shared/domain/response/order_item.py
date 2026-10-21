"""Order item response DTOs. The wire carries the REST field name `id` even though the proto field is `id` as well here (unlike category's `category_id`); timestamps are already formatted by the gRPC handlers, so the mapper passes them through unchanged. `deleted_at` is always present on the `...DeleteAt` shape: stores a pointer to a possibly-empty string, so an absent wrapper renders as `""`."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class OrderItemResponse:
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: int
    created_at: str
    updated_at: str


@dataclass
class OrderItemResponseDeleteAt:
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: int
    created_at: str
    updated_at: str
    deleted_at: str | None = None


# API response wrappers (kept close to the names) ----

OrderItemResponseApi = ApiResponse[OrderItemResponse]
OrderItemsResponse = ApiResponse[list[OrderItemResponse]]
OrderItemResponseDelete = ApiResponse[None]
OrderItemResponseAll = ApiResponse[None]
OrderItemResponsePagination = APIResponsePagination[list[OrderItemResponse]]
OrderItemResponsePaginationDeleteAt = APIResponsePagination[
    list[OrderItemResponseDeleteAt]
]


def pagination_meta(page: int, page_size: int, total_records: int) -> PaginationMeta:
    total_pages = math.ceil(total_records / page_size) if page_size else 0
    return PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total_records,
    )


__all__ = [
    "OrderItemResponse",
    "OrderItemResponseAll",
    "OrderItemResponseApi",
    "OrderItemResponseDelete",
    "OrderItemResponseDeleteAt",
    "OrderItemResponsePagination",
    "OrderItemResponsePaginationDeleteAt",
    "OrderItemsResponse",
    "pagination_meta",
]
