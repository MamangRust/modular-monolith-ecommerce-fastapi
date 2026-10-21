"""Category stats-by-id gRPC handler. The `*ById` price endpoints use the "Category monthly/yearly payment methods" messages, distinct from the base stats handler."""

from __future__ import annotations

from typing import Any

from pb.category import category_common_pb2
from pb.category.stats import category_stats_byid_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.category.handler.mapping import (
    fill_month_price,
    fill_monthly_total_price,
    fill_year_price,
    fill_yearly_total_price,
)
from service.category.service.interfaces import CategoryStatsByIdService
from service.category.service.service import SERVICE_NAME
from shared.errors import (
    err_grpc_category_invalid_id,
    err_grpc_category_invalid_month,
    err_grpc_category_invalid_year,
    err_grpc_category_stats,
)


class CategoryStatsByIdHandler(
    category_stats_byid_pb2_grpc.CategoryStatsByIdServiceServicer
):
    def __init__(self, service: CategoryStatsByIdService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("CategoryStatsByIdService.FindMonthlyTotalPricesById", SERVICE_NAME)
    async def FindMonthlyTotalPricesById(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        month = int(request.month)
        category_id = int(request.category_id)
        if year <= 0:
            raise err_grpc_category_invalid_year
        if month <= 0 or month > 12:
            raise err_grpc_category_invalid_month
        if category_id <= 0:
            raise err_grpc_category_invalid_id

        try:
            rows = await self._service.find_monthly_total_price_by_id(
                year, month, category_id
            )
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find monthly total prices by ID: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryMonthlyTotalPrice(
            status="success", message="Monthly sales retrieved successfully"
        )
        for row in rows:
            fill_monthly_total_price(response.data.add(), row)
        return response

    @grpc_method("CategoryStatsByIdService.FindYearlyTotalPricesById", SERVICE_NAME)
    async def FindYearlyTotalPricesById(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        category_id = int(request.category_id)
        if year <= 0:
            raise err_grpc_category_invalid_year
        if category_id <= 0:
            raise err_grpc_category_invalid_id

        try:
            rows = await self._service.find_yearly_total_price_by_id(year, category_id)
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find yearly total prices by ID: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryYearlyTotalPrice(
            status="success", message="Yearly payment methods retrieved successfully"
        )
        for row in rows:
            fill_yearly_total_price(response.data.add(), row)
        return response

    @grpc_method("CategoryStatsByIdService.FindMonthPriceById", SERVICE_NAME)
    async def FindMonthPriceById(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        category_id = int(request.category_id)
        if year <= 0:
            raise err_grpc_category_invalid_year
        if category_id <= 0:
            raise err_grpc_category_invalid_id

        try:
            rows = await self._service.find_month_price_by_id(year, category_id)
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find month price by ID: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryMonthPrice(
            status="success",
            message="Category monthly payment methods retrieved successfully",
        )
        for row in rows:
            fill_month_price(response.data.add(), row)
        return response

    @grpc_method("CategoryStatsByIdService.FindYearPriceById", SERVICE_NAME)
    async def FindYearPriceById(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        category_id = int(request.category_id)
        if year <= 0:
            raise err_grpc_category_invalid_year
        if category_id <= 0:
            raise err_grpc_category_invalid_id

        try:
            rows = await self._service.find_year_price_by_id(year, category_id)
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find year price by ID: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryYearPrice(
            status="success",
            message="Category yearly payment methods retrieved successfully",
        )
        for row in rows:
            fill_year_price(response.data.add(), row)
        return response


__all__ = ["CategoryStatsByIdHandler"]
