"""Category stats-by-merchant gRPC handler. The `*ByMerchant` price endpoints prefix their messages with "Merchant"."""

from __future__ import annotations

from typing import Any

from pb.category import category_common_pb2
from pb.category.stats import category_stats_bymerchant_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.category.handler.mapping import (
    fill_month_price,
    fill_monthly_total_price,
    fill_year_price,
    fill_yearly_total_price,
)
from service.category.service.interfaces import CategoryStatsByMerchantService
from service.category.service.service import SERVICE_NAME
from shared.errors import (
    err_grpc_category_invalid_merchant_id,
    err_grpc_category_invalid_month,
    err_grpc_category_invalid_year,
    err_grpc_category_stats,
)


class CategoryStatsByMerchantHandler(
    category_stats_bymerchant_pb2_grpc.CategoryStatsByMerchantServiceServicer
):
    def __init__(self, service: CategoryStatsByMerchantService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method(
        "CategoryStatsByMerchantService.FindMonthlyTotalPricesByMerchant", SERVICE_NAME
    )
    async def FindMonthlyTotalPricesByMerchant(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        month = int(request.month)
        merchant_id = int(request.merchant_id)
        if year <= 0:
            raise err_grpc_category_invalid_year
        if month <= 0 or month > 12:
            raise err_grpc_category_invalid_month
        if merchant_id <= 0:
            raise err_grpc_category_invalid_merchant_id

        try:
            rows = await self._service.find_monthly_total_price_by_merchant(
                year, month, merchant_id
            )
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find monthly total prices by merchant: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryMonthlyTotalPrice(
            status="success", message="Monthly sales retrieved successfully"
        )
        for row in rows:
            fill_monthly_total_price(response.data.add(), row)
        return response

    @grpc_method(
        "CategoryStatsByMerchantService.FindYearlyTotalPricesByMerchant", SERVICE_NAME
    )
    async def FindYearlyTotalPricesByMerchant(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        merchant_id = int(request.merchant_id)
        if year <= 0:
            raise err_grpc_category_invalid_year
        if merchant_id <= 0:
            raise err_grpc_category_invalid_merchant_id

        try:
            rows = await self._service.find_yearly_total_price_by_merchant(
                year, merchant_id
            )
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find yearly total prices by merchant: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryYearlyTotalPrice(
            status="success", message="Yearly payment methods retrieved successfully"
        )
        for row in rows:
            fill_yearly_total_price(response.data.add(), row)
        return response

    @grpc_method(
        "CategoryStatsByMerchantService.FindMonthPriceByMerchant", SERVICE_NAME
    )
    async def FindMonthPriceByMerchant(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        merchant_id = int(request.merchant_id)
        if year <= 0:
            raise err_grpc_category_invalid_year
        if merchant_id <= 0:
            raise err_grpc_category_invalid_merchant_id

        try:
            rows = await self._service.find_month_price_by_merchant(year, merchant_id)
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find month price by merchant: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryMonthPrice(
            status="success",
            message="Merchant monthly payment methods retrieved successfully",
        )
        for row in rows:
            fill_month_price(response.data.add(), row)
        return response

    @grpc_method("CategoryStatsByMerchantService.FindYearPriceByMerchant", SERVICE_NAME)
    async def FindYearPriceByMerchant(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        merchant_id = int(request.merchant_id)
        if year <= 0:
            raise err_grpc_category_invalid_year
        if merchant_id <= 0:
            raise err_grpc_category_invalid_merchant_id

        try:
            rows = await self._service.find_year_price_by_merchant(year, merchant_id)
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find year price by merchant: {exc}")
            raise err_grpc_category_stats from exc

        response = category_common_pb2.ApiResponseCategoryYearPrice(
            status="success",
            message="Merchant yearly payment methods retrieved successfully",
        )
        for row in rows:
            fill_year_price(response.data.add(), row)
        return response


__all__ = ["CategoryStatsByMerchantHandler"]
