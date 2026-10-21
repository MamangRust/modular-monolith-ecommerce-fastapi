"""Order stats-side REST mappers. Stats envelopes carry no pagination block (declares none)."""

from __future__ import annotations

from typing import Any

from shared.domain.response.order import (
    OrderMonthlyResponse,
    OrderMonthlyTotalRevenueResponse,
    OrderYearlyResponse,
    OrderYearlyTotalRevenueResponse,
)
from shared.domain.response.responses import ApiResponse
from shared.mapper.order.mapper import (
    map_order_monthly_response,
    map_order_monthly_total_revenue_response,
    map_order_yearly_response,
    map_order_yearly_total_revenue_response,
)


def to_order_monthly_price(pb: Any) -> OrderMonthlyResponse:
    return map_order_monthly_response(pb)


def to_order_monthly_prices(items: Any) -> list[OrderMonthlyResponse]:
    return [map_order_monthly_response(item) for item in items]


def to_order_yearly_price(pb: Any) -> OrderYearlyResponse:
    return map_order_yearly_response(pb)


def to_order_yearly_prices(items: Any) -> list[OrderYearlyResponse]:
    return [map_order_yearly_response(item) for item in items]


def to_response_order_monthly_total_revenue(
    pb: Any,
) -> OrderMonthlyTotalRevenueResponse:
    return map_order_monthly_total_revenue_response(pb)


def to_response_order_monthly_total_revenues(
    items: Any,
) -> list[OrderMonthlyTotalRevenueResponse]:
    return [map_order_monthly_total_revenue_response(item) for item in items]


def to_response_order_yearly_total_revenue(
    pb: Any,
) -> OrderYearlyTotalRevenueResponse:
    return map_order_yearly_total_revenue_response(pb)


def to_response_order_yearly_total_revenues(
    items: Any,
) -> list[OrderYearlyTotalRevenueResponse]:
    return [map_order_yearly_total_revenue_response(item) for item in items]


def to_api_response_monthly_order(
    pb: Any,
) -> ApiResponse[list[OrderMonthlyResponse]]:
    return ApiResponse[list[OrderMonthlyResponse]](
        status=pb.status,
        message=pb.message,
        data=to_order_monthly_prices(pb.data),
    )


def to_api_response_yearly_order(
    pb: Any,
) -> ApiResponse[list[OrderYearlyResponse]]:
    return ApiResponse[list[OrderYearlyResponse]](
        status=pb.status,
        message=pb.message,
        data=to_order_yearly_prices(pb.data),
    )


def to_api_response_monthly_total_revenue(
    pb: Any,
) -> ApiResponse[list[OrderMonthlyTotalRevenueResponse]]:
    return ApiResponse[list[OrderMonthlyTotalRevenueResponse]](
        status=pb.status,
        message=pb.message,
        data=to_response_order_monthly_total_revenues(pb.data),
    )


def to_api_response_yearly_total_revenue(
    pb: Any,
) -> ApiResponse[list[OrderYearlyTotalRevenueResponse]]:
    return ApiResponse[list[OrderYearlyTotalRevenueResponse]](
        status=pb.status,
        message=pb.message,
        data=to_response_order_yearly_total_revenues(pb.data),
    )


__all__ = [
    "to_api_response_monthly_order",
    "to_api_response_monthly_total_revenue",
    "to_api_response_yearly_order",
    "to_api_response_yearly_total_revenue",
    "to_order_monthly_price",
    "to_order_monthly_prices",
    "to_order_yearly_price",
    "to_order_yearly_prices",
    "to_response_order_monthly_total_revenue",
    "to_response_order_monthly_total_revenues",
    "to_response_order_yearly_total_revenue",
    "to_response_order_yearly_total_revenues",
]
