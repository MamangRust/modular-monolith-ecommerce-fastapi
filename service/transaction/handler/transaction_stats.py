"""transaction stats gRPC handler. registers a single `TransactionStatsService` carrying the eight global RPCs and a separate `TransactionStatsByMerchantService` for the by-merchant eight; the Python proto layout matches that split, so one handler class implements both servicers and is registered on both (order precedent)."""

from __future__ import annotations

from typing import Any

from pb.transaction import transaction_common_pb2
from pb.transaction.stats import (
    transaction_stats_bymerchant_pb2_grpc,
    transaction_stats_pb2_grpc,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.transaction.service.interfaces import (
    TransactionStatsByMerchantService,
    TransactionStatsService,
)
from service.transaction.service.service import SERVICE_NAME
from shared.domain.requests.transaction import (
    MonthAmountTransaction,
    MonthAmountTransactionMerchant,
    MonthMethodTransaction,
    MonthMethodTransactionMerchant,
    YearAmountTransactionMerchant,
    YearMethodTransactionMerchant,
)


class TransactionStatsHandler(
    transaction_stats_pb2_grpc.TransactionStatsServiceServicer,
    transaction_stats_bymerchant_pb2_grpc.TransactionStatsByMerchantServiceServicer,
):
    def __init__(
        self,
        stats: TransactionStatsService,
        stats_by_merchant: TransactionStatsByMerchantService,
        logger: Logger,
    ) -> None:
        self._stats = stats
        self._stats_by_merchant = stats_by_merchant
        self.logger = logger

    # ------------------------------------------------ global (TransactionStatsService)

    @grpc_method("TransactionStatsService.GetMonthlyAmountSuccess", SERVICE_NAME)
    async def GetMonthlyAmountSuccess(self, request: Any, context: Any) -> Any:
        rows = await self._stats.find_monthly_amount_success(
            MonthAmountTransaction(year=request.year, month=request.month)
        )
        response = transaction_common_pb2.ApiResponseTransactionMonthAmountSuccess(
            status="success",
            message="Successfully fetched monthly amount success stats",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                month=row.month,
                total_success=row.total_success,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method("TransactionStatsService.GetYearlyAmountSuccess", SERVICE_NAME)
    async def GetYearlyAmountSuccess(self, request: Any, context: Any) -> Any:
        rows = await self._stats.find_yearly_amount_success(int(request.year))
        response = transaction_common_pb2.ApiResponseTransactionYearAmountSuccess(
            status="success",
            message="Successfully fetched yearly amount success stats",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                total_success=row.total_success,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method("TransactionStatsService.GetMonthlyAmountFailed", SERVICE_NAME)
    async def GetMonthlyAmountFailed(self, request: Any, context: Any) -> Any:
        rows = await self._stats.find_monthly_amount_failed(
            MonthAmountTransaction(year=request.year, month=request.month)
        )
        response = transaction_common_pb2.ApiResponseTransactionMonthAmountFailed(
            status="success",
            message="Successfully fetched monthly amount failed stats",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                month=row.month,
                total_failed=row.total_failed,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method("TransactionStatsService.GetYearlyAmountFailed", SERVICE_NAME)
    async def GetYearlyAmountFailed(self, request: Any, context: Any) -> Any:
        rows = await self._stats.find_yearly_amount_failed(int(request.year))
        response = transaction_common_pb2.ApiResponseTransactionYearAmountFailed(
            status="success",
            message="Successfully fetched yearly amount failed stats",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                total_failed=row.total_failed,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method(
        "TransactionStatsService.GetMonthlyTransactionMethodSuccess", SERVICE_NAME
    )
    async def GetMonthlyTransactionMethodSuccess(
        self, request: Any, context: Any
    ) -> Any:
        rows = await self._stats.find_monthly_method_success(
            MonthMethodTransaction(year=request.year, month=request.month)
        )
        response = transaction_common_pb2.ApiResponseTransactionMonthPaymentMethod(
            status="success",
            message="Successfully fetched monthly transaction method success stats",
        )
        for row in rows:
            response.data.add(
                month=row.month,
                payment_method=row.payment_method,
                total_transactions=row.total_transactions,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method(
        "TransactionStatsService.GetYearlyTransactionMethodSuccess", SERVICE_NAME
    )
    async def GetYearlyTransactionMethodSuccess(
        self, request: Any, context: Any
    ) -> Any:
        rows = await self._stats.find_yearly_method_success(int(request.year))
        response = transaction_common_pb2.ApiResponseTransactionYearPaymentmethod(
            status="success",
            message="Successfully fetched yearly transaction method success stats",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                payment_method=row.payment_method,
                total_transactions=row.total_transactions,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method(
        "TransactionStatsService.GetMonthlyTransactionMethodFailed", SERVICE_NAME
    )
    async def GetMonthlyTransactionMethodFailed(
        self, request: Any, context: Any
    ) -> Any:
        rows = await self._stats.find_monthly_method_failed(
            MonthMethodTransaction(year=request.year, month=request.month)
        )
        response = transaction_common_pb2.ApiResponseTransactionMonthPaymentMethod(
            status="success",
            message="Successfully fetched monthly transaction method failed stats",
        )
        for row in rows:
            response.data.add(
                month=row.month,
                payment_method=row.payment_method,
                total_transactions=row.total_transactions,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method(
        "TransactionStatsService.GetYearlyTransactionMethodFailed", SERVICE_NAME
    )
    async def GetYearlyTransactionMethodFailed(
        self, request: Any, context: Any
    ) -> Any:
        rows = await self._stats.find_yearly_method_failed(int(request.year))
        response = transaction_common_pb2.ApiResponseTransactionYearPaymentmethod(
            status="success",
            message="Successfully fetched yearly transaction method failed stats",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                payment_method=row.payment_method,
                total_transactions=row.total_transactions,
                total_amount=row.total_amount,
            )
        return response

    # ------------------------------- by merchant (TransactionStatsByMerchantService)

    @grpc_method(
        "TransactionStatsByMerchantService.GetMonthlyAmountSuccessByMerchant",
        SERVICE_NAME,
    )
    async def GetMonthlyAmountSuccessByMerchant(
        self, request: Any, context: Any
    ) -> Any:
        rows = (
            await self._stats_by_merchant.find_monthly_amount_success_by_merchant(
                MonthAmountTransactionMerchant(
                    merchant_id=request.merchant_id,
                    year=request.year,
                    month=request.month,
                )
            )
        )
        response = transaction_common_pb2.ApiResponseTransactionMonthAmountSuccess(
            status="success",
            message="Successfully fetched monthly amount success stats by merchant",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                month=row.month,
                total_success=row.total_success,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method(
        "TransactionStatsByMerchantService.GetYearlyAmountSuccessByMerchant",
        SERVICE_NAME,
    )
    async def GetYearlyAmountSuccessByMerchant(
        self, request: Any, context: Any
    ) -> Any:
        rows = await self._stats_by_merchant.find_yearly_amount_success_by_merchant(
            YearAmountTransactionMerchant(
                merchant_id=request.merchant_id, year=request.year
            )
        )
        response = transaction_common_pb2.ApiResponseTransactionYearAmountSuccess(
            status="success",
            message="Successfully fetched yearly amount success stats by merchant",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                total_success=row.total_success,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method(
        "TransactionStatsByMerchantService.GetMonthlyAmountFailedByMerchant",
        SERVICE_NAME,
    )
    async def GetMonthlyAmountFailedByMerchant(
        self, request: Any, context: Any
    ) -> Any:
        rows = (
            await self._stats_by_merchant.find_monthly_amount_failed_by_merchant(
                MonthAmountTransactionMerchant(
                    merchant_id=request.merchant_id,
                    year=request.year,
                    month=request.month,
                )
            )
        )
        response = transaction_common_pb2.ApiResponseTransactionMonthAmountFailed(
            status="success",
            message="Successfully fetched monthly amount failed stats by merchant",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                month=row.month,
                total_failed=row.total_failed,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method(
        "TransactionStatsByMerchantService.GetYearlyAmountFailedByMerchant",
        SERVICE_NAME,
    )
    async def GetYearlyAmountFailedByMerchant(
        self, request: Any, context: Any
    ) -> Any:
        rows = await self._stats_by_merchant.find_yearly_amount_failed_by_merchant(
            YearAmountTransactionMerchant(
                merchant_id=request.merchant_id, year=request.year
            )
        )
        response = transaction_common_pb2.ApiResponseTransactionYearAmountFailed(
            status="success",
            message="Successfully fetched yearly amount failed stats by merchant",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                total_failed=row.total_failed,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method(
        "TransactionStatsByMerchantService."
        "GetMonthlyTransactionMethodByMerchantSuccess",
        SERVICE_NAME,
    )
    async def GetMonthlyTransactionMethodByMerchantSuccess(
        self, request: Any, context: Any
    ) -> Any:
        rows = (
            await self._stats_by_merchant.find_monthly_method_success_by_merchant(
                MonthMethodTransactionMerchant(
                    merchant_id=request.merchant_id,
                    year=request.year,
                    month=request.month,
                )
            )
        )
        response = transaction_common_pb2.ApiResponseTransactionMonthPaymentMethod(
            status="success",
            message="Successfully fetched monthly transaction method success stats by merchant",
        )
        for row in rows:
            response.data.add(
                month=row.month,
                payment_method=row.payment_method,
                total_transactions=row.total_transactions,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method(
        "TransactionStatsByMerchantService."
        "GetYearlyTransactionMethodByMerchantSuccess",
        SERVICE_NAME,
    )
    async def GetYearlyTransactionMethodByMerchantSuccess(
        self, request: Any, context: Any
    ) -> Any:
        rows = (
            await self._stats_by_merchant.find_yearly_method_success_by_merchant(
                YearMethodTransactionMerchant(
                    merchant_id=request.merchant_id, year=request.year
                )
            )
        )
        response = transaction_common_pb2.ApiResponseTransactionYearPaymentmethod(
            status="success",
            message="Successfully fetched yearly transaction method success stats by merchant",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                payment_method=row.payment_method,
                total_transactions=row.total_transactions,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method(
        "TransactionStatsByMerchantService."
        "GetMonthlyTransactionMethodByMerchantFailed",
        SERVICE_NAME,
    )
    async def GetMonthlyTransactionMethodByMerchantFailed(
        self, request: Any, context: Any
    ) -> Any:
        rows = (
            await self._stats_by_merchant.find_monthly_method_failed_by_merchant(
                MonthMethodTransactionMerchant(
                    merchant_id=request.merchant_id,
                    year=request.year,
                    month=request.month,
                )
            )
        )
        response = transaction_common_pb2.ApiResponseTransactionMonthPaymentMethod(
            status="success",
            message="Successfully fetched monthly transaction method failed stats by merchant",
        )
        for row in rows:
            response.data.add(
                month=row.month,
                payment_method=row.payment_method,
                total_transactions=row.total_transactions,
                total_amount=row.total_amount,
            )
        return response

    @grpc_method(
        "TransactionStatsByMerchantService."
        "GetYearlyTransactionMethodByMerchantFailed",
        SERVICE_NAME,
    )
    async def GetYearlyTransactionMethodByMerchantFailed(
        self, request: Any, context: Any
    ) -> Any:
        rows = await self._stats_by_merchant.find_yearly_method_failed_by_merchant(
            YearMethodTransactionMerchant(
                merchant_id=request.merchant_id, year=request.year
            )
        )
        response = transaction_common_pb2.ApiResponseTransactionYearPaymentmethod(
            status="success",
            message="Successfully fetched yearly transaction method failed stats by merchant",
        )
        for row in rows:
            response.data.add(
                year=row.year,
                payment_method=row.payment_method,
                total_transactions=row.total_transactions,
                total_amount=row.total_amount,
            )
        return response


__all__ = ["TransactionStatsHandler"]
