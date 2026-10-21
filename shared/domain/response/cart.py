"""Cart response DTOs. Field names match the REST DTOs exactly. The proto field is `id` and the REST field is also `id`; `image` (not `image_product`) is the wire name. Date strings are already formatted `%Y-%m-%d` by the gRPC handlers, so the mapper passes them through unchanged."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class CartResponse:
    id: int
    user_id: int
    product_id: int
    name: str
    price: int
    image: str
    quantity: int
    weight: int
    created_at: str
    updated_at: str


# API response wrappers (kept close to the names) ----

CartResponseApi = ApiResponse[CartResponse]
CartResponseDelete = ApiResponse[None]
CartResponseAll = ApiResponse[None]
CartResponses = ApiResponse[list[CartResponse]]
CartResponsePagination = APIResponsePagination[list[CartResponse]]


def pagination_meta(page: int, page_size: int, total_records: int) -> PaginationMeta:
    total_pages = math.ceil(total_records / page_size) if page_size else 0
    return PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total_records,
    )


__all__ = [
    "CartResponse",
    "CartResponseAll",
    "CartResponseApi",
    "CartResponseDelete",
    "CartResponsePagination",
    "CartResponses",
    "pagination_meta",
]
