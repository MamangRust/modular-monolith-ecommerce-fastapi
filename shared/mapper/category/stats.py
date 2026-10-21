"""Category stats response mapping.

Four list shapes (month price / year price / monthly total / yearly total),
each wrapped in a bare `ApiResponse` envelope (no pagination)."""

from __future__ import annotations

from typing import Any

from shared.domain.response.category import (
    CategoriesMonthlyTotalPriceResponse,
    CategoriesYearlyTotalPriceResponse,
    CategoryMonthPriceResponse,
    CategoryYearPriceResponse,
)
from shared.domain.response.responses import ApiResponse


def map_category_month_price(pb: Any) -> CategoryMonthPriceResponse:
    return CategoryMonthPriceResponse(
        month=pb.month,
        category_id=int(pb.category_id),
        category_name=pb.category_name,
        order_count=int(pb.order_count),
        items_sold=int(pb.items_sold),
        total_revenue=int(pb.total_revenue),
    )


def map_category_month_prices(
    items: Any,
) -> list[CategoryMonthPriceResponse]:
    return [map_category_month_price(item) for item in items]


def map_category_year_price(pb: Any) -> CategoryYearPriceResponse:
    return CategoryYearPriceResponse(
        year=pb.year,
        category_id=int(pb.category_id),
        category_name=pb.category_name,
        order_count=int(pb.order_count),
        items_sold=int(pb.items_sold),
        total_revenue=int(pb.total_revenue),
        unique_products_sold=int(pb.unique_products_sold),
    )


def map_category_year_prices(
    items: Any,
) -> list[CategoryYearPriceResponse]:
    return [map_category_year_price(item) for item in items]


def map_categories_monthly_total_price(
    pb: Any,
) -> CategoriesMonthlyTotalPriceResponse:
    return CategoriesMonthlyTotalPriceResponse(
        year=pb.year,
        month=pb.month,
        total_revenue=int(pb.total_revenue),
    )


def map_categories_monthly_total_prices(
    items: Any,
) -> list[CategoriesMonthlyTotalPriceResponse]:
    return [map_categories_monthly_total_price(item) for item in items]


def map_categories_yearly_total_price(
    pb: Any,
) -> CategoriesYearlyTotalPriceResponse:
    return CategoriesYearlyTotalPriceResponse(
        year=pb.year,
        total_revenue=int(pb.total_revenue),
    )


def map_categories_yearly_total_prices(
    items: Any,
) -> list[CategoriesYearlyTotalPriceResponse]:
    return [map_categories_yearly_total_price(item) for item in items]


def to_api_response_category_month_price(
    pb: Any,
) -> ApiResponse[list[CategoryMonthPriceResponse]]:
    return ApiResponse[list[CategoryMonthPriceResponse]](
        status=pb.status,
        message=pb.message,
        data=map_category_month_prices(pb.data),
    )


def to_api_response_category_year_price(
    pb: Any,
) -> ApiResponse[list[CategoryYearPriceResponse]]:
    return ApiResponse[list[CategoryYearPriceResponse]](
        status=pb.status,
        message=pb.message,
        data=map_category_year_prices(pb.data),
    )


def to_api_response_category_monthly_total_price(
    pb: Any,
) -> ApiResponse[list[CategoriesMonthlyTotalPriceResponse]]:
    return ApiResponse[list[CategoriesMonthlyTotalPriceResponse]](
        status=pb.status,
        message=pb.message,
        data=map_categories_monthly_total_prices(pb.data),
    )


def to_api_response_category_yearly_total_price(
    pb: Any,
) -> ApiResponse[list[CategoriesYearlyTotalPriceResponse]]:
    return ApiResponse[list[CategoriesYearlyTotalPriceResponse]](
        status=pb.status,
        message=pb.message,
        data=map_categories_yearly_total_prices(pb.data),
    )


__all__ = [
    "map_categories_monthly_total_price",
    "map_categories_monthly_total_prices",
    "map_categories_yearly_total_price",
    "map_categories_yearly_total_prices",
    "map_category_month_price",
    "map_category_month_prices",
    "map_category_year_price",
    "map_category_year_prices",
    "to_api_response_category_month_price",
    "to_api_response_category_monthly_total_price",
    "to_api_response_category_year_price",
    "to_api_response_category_yearly_total_price",
]
