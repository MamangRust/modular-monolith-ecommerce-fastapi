"""Order stats REST routes. All routes are static (no path parameters), so registration order does not matter. Query params default to 0, matching `strconv.Atoi` on an absent param; the handler forwards the zero values and the domain service rejects them exactly. The gateway does not cache."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.order.handler import OrderHandler
from shared.domain.response.order import (
    OrderMonthlyApi,
    OrderMonthlyTotalRevenueApi,
    OrderYearlyApi,
    OrderYearlyTotalRevenueApi,
)

router = APIRouter(prefix="/api/order", tags=["order-stats"])


def get_order_handler(request: Request) -> OrderHandler:
    return OrderHandler(request.app.state.connections)


# ---- total revenue ----


@router.get("/monthly-total-revenue")
async def find_monthly_total_revenue(
    request: Request,
    year: int = 0,
    month: int = 0,
) -> OrderMonthlyTotalRevenueApi:
    return await get_order_handler(request).find_monthly_total_revenue(year, month)


@router.get("/yearly-total-revenue")
async def find_yearly_total_revenue(
    request: Request,
    year: int = 0,
) -> OrderYearlyTotalRevenueApi:
    return await get_order_handler(request).find_yearly_total_revenue(year)


@router.get("/merchant/monthly-total-revenue")
async def find_monthly_total_revenue_by_merchant(
    request: Request,
    year: int = 0,
    month: int = 0,
    merchant_id: int = 0,
) -> OrderMonthlyTotalRevenueApi:
    return await get_order_handler(request).find_monthly_total_revenue_by_merchant(year, month, merchant_id)


@router.get("/merchant/yearly-total-revenue")
async def find_yearly_total_revenue_by_merchant(
    request: Request,
    year: int = 0,
    merchant_id: int = 0,
) -> OrderYearlyTotalRevenueApi:
    return await get_order_handler(request).find_yearly_total_revenue_by_merchant(year, merchant_id)


# ---- revenue ----


@router.get("/monthly-revenue")
async def find_monthly_revenue(
    request: Request,
    year: int = 0,
) -> OrderMonthlyApi:
    return await get_order_handler(request).find_monthly_revenue(year)


@router.get("/yearly-revenue")
async def find_yearly_revenue(
    request: Request,
    year: int = 0,
) -> OrderYearlyApi:
    return await get_order_handler(request).find_yearly_revenue(year)


@router.get("/merchant/monthly-revenue")
async def find_monthly_revenue_by_merchant(
    request: Request,
    year: int = 0,
    merchant_id: int = 0,
) -> OrderMonthlyApi:
    return await get_order_handler(request).find_monthly_revenue_by_merchant(year, merchant_id)


@router.get("/merchant/yearly-revenue")
async def find_yearly_revenue_by_merchant(
    request: Request,
    year: int = 0,
    merchant_id: int = 0,
) -> OrderYearlyApi:
    return await get_order_handler(request).find_yearly_revenue_by_merchant(year, merchant_id)


__all__ = ["router"]
