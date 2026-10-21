"""Category response DTOs. The wire carries the REST field name `id` even though the proto field is `category_id`; date strings are already formatted by the gRPC handlers, so the mapper passes them through unchanged. The stats envelopes are kept as aliases of the generic `ApiResponse` wrapper, matching the banner module's shape."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class CategoryResponse:
    id: int
    name: str
    description: str
    slug_category: str
    image_category: str
    created_at: str
    updated_at: str


@dataclass
class CategoryResponseDeleteAt:
    id: int
    name: str
    description: str
    slug_category: str
    image_category: str
    created_at: str
    updated_at: str
    deleted_at: str | None = None


@dataclass
class CategoryMonthPriceResponse:
    month: str
    category_id: int
    category_name: str
    order_count: int
    items_sold: int
    total_revenue: int


@dataclass
class CategoryYearPriceResponse:
    year: str
    category_id: int
    category_name: str
    order_count: int
    items_sold: int
    total_revenue: int
    unique_products_sold: int


@dataclass
class CategoriesMonthlyTotalPriceResponse:
    year: str
    month: str
    total_revenue: int


@dataclass
class CategoriesYearlyTotalPriceResponse:
    year: str
    total_revenue: int


# API response wrappers (kept close to the names) ----

CategoryResponseAll = ApiResponse[None]
CategoryResponseDelete = ApiResponse[None]
CategoryResponseApi = ApiResponse[CategoryResponse]
CategoryResponseDeleteAtApi = ApiResponse[CategoryResponseDeleteAt]
CategoriesResponse = ApiResponse[list[CategoryResponse]]
CategoryResponsePagination = APIResponsePagination[list[CategoryResponse]]
CategoryResponsePaginationDeleteAt = APIResponsePagination[
    list[CategoryResponseDeleteAt]
]

CategoryMonthPriceApi = ApiResponse[list[CategoryMonthPriceResponse]]
CategoryYearPriceApi = ApiResponse[list[CategoryYearPriceResponse]]
CategoryMonthlyTotalPriceApi = ApiResponse[list[CategoriesMonthlyTotalPriceResponse]]
CategoryYearlyTotalPriceApi = ApiResponse[list[CategoriesYearlyTotalPriceResponse]]


def pagination_meta(page: int, page_size: int, total_records: int) -> PaginationMeta:
    total_pages = math.ceil(total_records / page_size) if page_size else 0
    return PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total_records,
    )


__all__ = [
    "CategoriesMonthlyTotalPriceResponse",
    "CategoriesResponse",
    "CategoriesYearlyTotalPriceResponse",
    "CategoryMonthPriceApi",
    "CategoryMonthPriceResponse",
    "CategoryMonthlyTotalPriceApi",
    "CategoryResponse",
    "CategoryResponseAll",
    "CategoryResponseApi",
    "CategoryResponseDelete",
    "CategoryResponseDeleteAt",
    "CategoryResponseDeleteAtApi",
    "CategoryResponsePagination",
    "CategoryResponsePaginationDeleteAt",
    "CategoryYearPriceApi",
    "CategoryYearPriceResponse",
    "CategoryYearlyTotalPriceApi",
    "pagination_meta",
]
