"""Category stats REST routes. All routes are static (no path parameters), so registration order does not matter here."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.category.handler import CategoryHandler
from shared.domain.response.category import (
    CategoriesMonthlyTotalPriceResponse,
    CategoriesYearlyTotalPriceResponse,
    CategoryMonthPriceResponse,
    CategoryYearPriceResponse,
)
from shared.domain.response.responses import ApiResponse

router = APIRouter(prefix="/api/category-stats", tags=["category-stats"])


def get_category_handler(request: Request) -> CategoryHandler:
    return CategoryHandler(
        request.app.state.connections, request.app.state.upload_image
    )


# ---- total pricing ----


@router.get("/monthly-total-pricing")
async def find_month_total_price(
    request: Request,
    year: int = 0,
    month: int = 0,
) -> ApiResponse[list[CategoriesMonthlyTotalPriceResponse]]:
    return await get_category_handler(request).find_month_total_price(year, month)


@router.get("/yearly-total-pricing")
async def find_year_total_price(
    request: Request,
    year: int = 0,
) -> ApiResponse[list[CategoriesYearlyTotalPriceResponse]]:
    return await get_category_handler(request).find_year_total_price(year)


@router.get("/merchant/monthly-total-pricing")
async def find_month_total_price_by_merchant(
    request: Request,
    year: int = 0,
    month: int = 0,
    merchant_id: int = 0,
) -> ApiResponse[list[CategoriesMonthlyTotalPriceResponse]]:
    return await get_category_handler(request).find_month_total_price_by_merchant(
        year, month, merchant_id
    )


@router.get("/merchant/yearly-total-pricing")
async def find_year_total_price_by_merchant(
    request: Request,
    year: int = 0,
    merchant_id: int = 0,
) -> ApiResponse[list[CategoriesYearlyTotalPriceResponse]]:
    return await get_category_handler(request).find_year_total_price_by_merchant(
        year, merchant_id
    )


@router.get("/mycategory/monthly-total-pricing")
async def find_month_total_price_by_id(
    request: Request,
    year: int = 0,
    month: int = 0,
    category_id: int = 0,
) -> ApiResponse[list[CategoriesMonthlyTotalPriceResponse]]:
    return await get_category_handler(request).find_month_total_price_by_id(
        year, month, category_id
    )


@router.get("/mycategory/yearly-total-pricing")
async def find_year_total_price_by_id(
    request: Request,
    year: int = 0,
    category_id: int = 0,
) -> ApiResponse[list[CategoriesYearlyTotalPriceResponse]]:
    return await get_category_handler(request).find_year_total_price_by_id(
        year, category_id
    )


# ---- pricing ----


@router.get("/monthly-pricing")
async def find_month_price(
    request: Request,
    year: int = 0,
    month: int = 0,
) -> ApiResponse[list[CategoryMonthPriceResponse]]:
    return await get_category_handler(request).find_month_price(year)


@router.get("/yearly-pricing")
async def find_year_price(
    request: Request,
    year: int = 0,
) -> ApiResponse[list[CategoryYearPriceResponse]]:
    return await get_category_handler(request).find_year_price(year)


@router.get("/merchant/monthly-pricing")
async def find_month_price_by_merchant(
    request: Request,
    year: int = 0,
    merchant_id: int = 0,
) -> ApiResponse[list[CategoryMonthPriceResponse]]:
    return await get_category_handler(request).find_month_price_by_merchant(
        year, merchant_id
    )


@router.get("/merchant/yearly-pricing")
async def find_year_price_by_merchant(
    request: Request,
    year: int = 0,
    merchant_id: int = 0,
) -> ApiResponse[list[CategoryYearPriceResponse]]:
    return await get_category_handler(request).find_year_price_by_merchant(
        year, merchant_id
    )


@router.get("/mycategory/monthly-pricing")
async def find_month_price_by_id(
    request: Request,
    year: int = 0,
    category_id: int = 0,
) -> ApiResponse[list[CategoryMonthPriceResponse]]:
    return await get_category_handler(request).find_month_price_by_id(year, category_id)


@router.get("/mycategory/yearly-pricing")
async def find_year_price_by_id(
    request: Request,
    year: int = 0,
    category_id: int = 0,
) -> ApiResponse[list[CategoryYearPriceResponse]]:
    return await get_category_handler(request).find_year_price_by_id(year, category_id)


__all__ = ["router"]
