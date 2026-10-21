"""Category stats gRPC handler. Note the verbatim messages: the total-price endpoints say "sales" while the price endpoints say "payment methods" — kept as-is."""

from __future__ import annotations

from typing import Any

from pb.category import category_common_pb2
from pb.category.stats import category_stats_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.category.handler.mapping import (
    fill_month_price,
    fill_monthly_total_price,
    fill_year_price,
    fill_yearly_total_price,
)
from service.category.service.interfaces import CategoryStatsService
from service.category.service.service import SERVICE_NAME
from shared.errors import (
    err_grpc_category_invalid_month,
    err_grpc_category_invalid_year,
    err_grpc_category_stats,
)


class CategoryStatsHandler(category_stats_pb2_grpc.CategoryStatsServiceServicer):
    def __init__(self, service: CategoryStatsService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("CategoryStatsService.FindMonthlyTotalPrices", SERVICE_NAME)
    async def FindMonthlyTotalPrices(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        month = int(request.month)
        if year <= 0:
            raise err_grpc_category_invalid_year
        if month <= 0 or month > 12:
            raise err_grpc_category_invalid_month

        try:
            rows = await self._service.find_monthly_total_price(year, month)
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find monthly total prices: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryMonthlyTotalPrice(
            status="success", message="Monthly sales retrieved successfully"
        )
        for row in rows:
            fill_monthly_total_price(response.data.add(), row)
        return response

    @grpc_method("CategoryStatsService.FindYearlyTotalPrices", SERVICE_NAME)
    async def FindYearlyTotalPrices(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        if year <= 0:
            raise err_grpc_category_invalid_year

        try:
            rows = await self._service.find_yearly_total_price(year)
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find yearly total prices: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryYearlyTotalPrice(
            status="success", message="Yearly payment methods retrieved successfully"
        )
        for row in rows:
            fill_yearly_total_price(response.data.add(), row)
        return response

    @grpc_method("CategoryStatsService.FindMonthPrice", SERVICE_NAME)
    async def FindMonthPrice(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        if year <= 0:
            raise err_grpc_category_invalid_year

        try:
            rows = await self._service.find_month_price(year)
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find month price: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryMonthPrice(
            status="success", message="Monthly payment methods retrieved successfully"
        )
        for row in rows:
            fill_month_price(response.data.add(), row)
        return response

    @grpc_method("CategoryStatsService.FindYearPrice", SERVICE_NAME)
    async def FindYearPrice(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        if year <= 0:
            raise err_grpc_category_invalid_year

        try:
            rows = await self._service.find_year_price(year)
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find year price: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryYearPrice(
            status="success", message="Yearly payment methods retrieved successfully"
        )
        for row in rows:
            fill_year_price(response.data.add(), row)
        return response


__all__ = ["CategoryStatsHandler"]
