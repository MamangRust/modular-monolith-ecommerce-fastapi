"""order stats gRPC handler. registers a single `OrderStatsService` carrying all eight stats RPCs (global + by-merchant). The Python proto splits them across `OrderStatsService` and `OrderStatsByMerchantService`, so one handler class implements both servicers and is registered on both (proto-layout normalisation; RPC surface unchanged). `OrderMonthlyTotalRevenueResponse` also carries `order_count`/`total_items_sold` and `OrderYearlyResponse` carries `active_cashiers`, but never sets them, so leaves them at their zero value."""

from __future__ import annotations

from typing import Any

from pb.order import order_common_pb2
from pb.order.stats import (
    order_stats_pb2_grpc,
    order_statsbymerchant_pb2_grpc,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.order.service.interfaces import (
    OrderStatsByMerchantService,
    OrderStatsService,
)
from service.order.service.service import SERVICE_NAME
from shared.domain.requests.order import (
    MonthOrderMerchant,
    MonthTotalRevenue,
    MonthTotalRevenueMerchant,
    YearOrderMerchant,
    YearTotalRevenueMerchant,
)
from shared.errors.order_errors import (
    err_grpc_order_invalid_id,
    err_grpc_order_invalid_merchant_id,
    err_grpc_order_invalid_month,
    err_grpc_order_invalid_year,
)


class OrderStatsHandler(
    order_stats_pb2_grpc.OrderStatsServiceServicer,
    order_statsbymerchant_pb2_grpc.OrderStatsByMerchantServiceServicer,
):
    def __init__(
        self,
        stats: OrderStatsService,
        stats_by_merchant: OrderStatsByMerchantService,
        logger: Logger,
    ) -> None:
        self._stats = stats
        self._stats_by_merchant = stats_by_merchant
        self.logger = logger

    # ------------------------------------------------------------ global stats

    @grpc_method("OrderStatsService.FindMonthlyTotalRevenue", SERVICE_NAME)
    async def FindMonthlyTotalRevenue(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        month = int(request.month)
        if year <= 0:
            raise err_grpc_order_invalid_year
        if month <= 0 or month > 12:
            raise err_grpc_order_invalid_month

        rows = await self._stats.find_monthly_total_revenue(
            MonthTotalRevenue(year=year, month=month)
        )
        response = order_common_pb2.ApiResponseOrderMonthlyTotalRevenue(
            status="success", message="Monthly sales retrieved successfully"
        )
        for row in rows:
            item = response.data.add()
            item.year = row.year
            item.month = row.month
            item.total_revenue = int(row.total_revenue)
        return response

    @grpc_method("OrderStatsService.FindYearlyTotalRevenue", SERVICE_NAME)
    async def FindYearlyTotalRevenue(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        if year <= 0:
            raise err_grpc_order_invalid_year

        rows = await self._stats.find_yearly_total_revenue(year)
        response = order_common_pb2.ApiResponseOrderYearlyTotalRevenue(
            status="success",
            message="Yearly payment methods retrieved successfully",
        )
        for row in rows:
            item = response.data.add()
            item.year = row.year
            item.total_revenue = int(row.total_revenue)
        return response

    @grpc_method("OrderStatsService.FindMonthlyRevenue", SERVICE_NAME)
    async def FindMonthlyRevenue(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        if year <= 0:
            raise err_grpc_order_invalid_id

        rows = await self._stats.find_monthly_order(year)
        response = order_common_pb2.ApiResponseOrderMonthly(
            status="success", message="Monthly revenue data retrieved"
        )
        for row in rows:
            item = response.data.add()
            item.month = row.month
            item.order_count = int(row.order_count)
            item.total_revenue = int(row.total_revenue)
            item.total_items_sold = int(row.total_items_sold)
        return response

    @grpc_method("OrderStatsService.FindYearlyRevenue", SERVICE_NAME)
    async def FindYearlyRevenue(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        if year <= 0:
            raise err_grpc_order_invalid_id

        rows = await self._stats.find_yearly_order(year)
        response = order_common_pb2.ApiResponseOrderYearly(
            status="success", message="Yearly revenue data retrieved"
        )
        for row in rows:
            item = response.data.add()
            item.year = row.year
            item.order_count = int(row.order_count)
            item.total_revenue = int(row.total_revenue)
            item.total_items_sold = int(row.total_items_sold)
            item.unique_products_sold = int(row.unique_products_sold)
        return response

    # --------------------------------------------------- by-merchant stats

    @grpc_method(
        "OrderStatsByMerchantService.FindMonthlyTotalRevenueByMerchant",
        SERVICE_NAME,
    )
    async def FindMonthlyTotalRevenueByMerchant(
        self, request: Any, context: Any
    ) -> Any:
        year = int(request.year)
        month = int(request.month)
        merchant_id = int(request.merchant_id)
        if year <= 0:
            raise err_grpc_order_invalid_year
        if month <= 0 or month > 12:
            raise err_grpc_order_invalid_month
        if merchant_id <= 0:
            raise err_grpc_order_invalid_merchant_id

        rows = await self._stats_by_merchant.find_monthly_total_revenue_by_merchant(
            MonthTotalRevenueMerchant(
                merchant_id=merchant_id, year=year, month=month
            )
        )
        response = order_common_pb2.ApiResponseOrderMonthlyTotalRevenue(
            status="success", message="Monthly sales retrieved successfully"
        )
        for row in rows:
            item = response.data.add()
            item.year = row.year
            item.month = row.month
            item.total_revenue = int(row.total_revenue)
        return response

    @grpc_method(
        "OrderStatsByMerchantService.FindYearlyTotalRevenueByMerchant",
        SERVICE_NAME,
    )
    async def FindYearlyTotalRevenueByMerchant(
        self, request: Any, context: Any
    ) -> Any:
        year = int(request.year)
        merchant_id = int(request.merchant_id)
        if year <= 0:
            raise err_grpc_order_invalid_year
        if merchant_id <= 0:
            raise err_grpc_order_invalid_merchant_id

        rows = await self._stats_by_merchant.find_yearly_total_revenue_by_merchant(
            YearTotalRevenueMerchant(merchant_id=merchant_id, year=year)
        )
        response = order_common_pb2.ApiResponseOrderYearlyTotalRevenue(
            status="success",
            message="Yearly payment methods retrieved successfully",
        )
        for row in rows:
            item = response.data.add()
            item.year = row.year
            item.total_revenue = int(row.total_revenue)
        return response

    @grpc_method(
        "OrderStatsByMerchantService.FindMonthlyRevenueByMerchant", SERVICE_NAME
    )
    async def FindMonthlyRevenueByMerchant(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        merchant_id = int(request.merchant_id)
        if year <= 0:
            raise err_grpc_order_invalid_year
        if merchant_id <= 0:
            raise err_grpc_order_invalid_merchant_id

        rows = await self._stats_by_merchant.find_monthly_order_by_merchant(
            MonthOrderMerchant(merchant_id=merchant_id, year=year)
        )
        response = order_common_pb2.ApiResponseOrderMonthly(
            status="success", message="Monthly revenue by merchant data retrieved"
        )
        for row in rows:
            item = response.data.add()
            item.month = row.month
            item.order_count = int(row.order_count)
            item.total_revenue = int(row.total_revenue)
            item.total_items_sold = int(row.total_items_sold)
        return response

    @grpc_method(
        "OrderStatsByMerchantService.FindYearlyRevenueByMerchant", SERVICE_NAME
    )
    async def FindYearlyRevenueByMerchant(self, request: Any, context: Any) -> Any:
        year = int(request.year)
        merchant_id = int(request.merchant_id)
        if year <= 0:
            raise err_grpc_order_invalid_year
        # uses the generic invalid-id sentinel here (not invalid merchant).
        if merchant_id <= 0:
            raise err_grpc_order_invalid_id

        rows = await self._stats_by_merchant.find_yearly_order_by_merchant(
            YearOrderMerchant(merchant_id=merchant_id, year=year)
        )
        response = order_common_pb2.ApiResponseOrderYearly(
            status="success",
            message="Yearly revenue by merchant data retrieved",
        )
        for row in rows:
            item = response.data.add()
            item.year = row.year
            item.order_count = int(row.order_count)
            item.total_revenue = int(row.total_revenue)
            item.total_items_sold = int(row.total_items_sold)
            item.unique_products_sold = int(row.unique_products_sold)
        return response


__all__ = ["OrderStatsHandler"]
