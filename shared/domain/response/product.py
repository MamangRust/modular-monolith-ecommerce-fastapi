"""product response DTOs. Field names match the REST DTOs exactly. Two shapes, the proto: - `ProductResponse` (Create/Update/FindById, FindAll list); - `ProductResponseDeleteAt` (active/trashed lists, trash/restore). `deleted_at` follows the conditional convention: `""` for a live row, the formatted timestamp only when actually trashed. Timestamps are already formatted by the gRPC handlers (`.mmm`), so the mapper passes them through unchanged. `rating` is a `float` (the proto field is a float; the request carries an int)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class ProductResponse:
    id: int
    merchant_id: int
    category_id: int
    name: str
    description: str
    price: int
    count_in_stock: int
    brand: str
    weight: int
    rating: float
    slug_product: str
    image_product: str
    created_at: str
    updated_at: str


@dataclass
class ProductResponseDeleteAt:
    id: int
    merchant_id: int
    category_id: int
    name: str
    description: str
    price: int
    count_in_stock: int
    brand: str
    weight: int
    rating: float
    slug_product: str
    image_product: str
    created_at: str
    updated_at: str
    deleted_at: str = ""


# API response wrappers (kept close to the names) ----

ProductResponseApi = ApiResponse[ProductResponse]
ProductResponseDeleteAtApi = ApiResponse[ProductResponseDeleteAt]
ProductResponses = ApiResponse[list[ProductResponse]]
ProductResponsePagination = APIResponsePagination[list[ProductResponse]]
ProductResponsePaginationDeleteAt = APIResponsePagination[
    list[ProductResponseDeleteAt]
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
    "ProductResponse",
    "ProductResponseApi",
    "ProductResponseDeleteAt",
    "ProductResponseDeleteAtApi",
    "ProductResponsePagination",
    "ProductResponsePaginationDeleteAt",
    "ProductResponses",
    "pagination_meta",
]
