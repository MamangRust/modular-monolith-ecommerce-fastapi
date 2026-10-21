"""transaction stats-by-merchant service."""

from __future__ import annotations

from pkg.database.schema.transaction import (
    GetMonthlyAmountTransactionFailedRow,
    GetMonthlyAmountTransactionSuccessRow,
    GetMonthlyTransactionMethodsRow,
    GetYearlyAmountTransactionFailedRow,
    GetYearlyAmountTransactionSuccessRow,
    GetYearlyTransactionMethodsRow,
)
from pkg.logger.logger import Logger
from service.transaction.redis.interfaces import TransactionStatsByMerchantCache
from service.transaction.repository.interfaces import (
    TransactionStatsByMerchantRepository,
)
from shared.domain.requests.transaction import (
    MonthAmountTransactionMerchant,
    MonthMethodTransactionMerchant,
    YearAmountTransactionMerchant,
    YearMethodTransactionMerchant,
)
from shared.observability import Observability


class TransactionStatsByMerchantServiceImpl:
    def __init__(
        self,
        repo: TransactionStatsByMerchantRepository,
        cache: TransactionStatsByMerchantCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_monthly_amount_success_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionSuccessRow]:
        with self._obs.span(
            "transaction.stats.find_monthly_amount_success_by_merchant",
            merchant_id=request.merchant_id,
            year=request.year,
            month=request.month,
        ):
            cached = await self._cache.get_monthly_amount_success_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_amount_success_by_merchant(request)
            await self._cache.set_monthly_amount_success_by_merchant(request, rows)
            return rows

    async def find_yearly_amount_success_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionSuccessRow]:
        with self._obs.span(
            "transaction.stats.find_yearly_amount_success_by_merchant",
            merchant_id=request.merchant_id,
            year=request.year,
        ):
            cached = await self._cache.get_yearly_amount_success_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_amount_success_by_merchant(request)
            await self._cache.set_yearly_amount_success_by_merchant(request, rows)
            return rows

    async def find_monthly_amount_failed_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionFailedRow]:
        with self._obs.span(
            "transaction.stats.find_monthly_amount_failed_by_merchant",
            merchant_id=request.merchant_id,
            year=request.year,
            month=request.month,
        ):
            cached = await self._cache.get_monthly_amount_failed_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_amount_failed_by_merchant(request)
            await self._cache.set_monthly_amount_failed_by_merchant(request, rows)
            return rows

    async def find_yearly_amount_failed_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionFailedRow]:
        with self._obs.span(
            "transaction.stats.find_yearly_amount_failed_by_merchant",
            merchant_id=request.merchant_id,
            year=request.year,
        ):
            cached = await self._cache.get_yearly_amount_failed_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_amount_failed_by_merchant(request)
            await self._cache.set_yearly_amount_failed_by_merchant(request, rows)
            return rows

    async def find_monthly_method_success_by_merchant(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow]:
        with self._obs.span(
            "transaction.stats.find_monthly_method_success_by_merchant",
            merchant_id=request.merchant_id,
            year=request.year,
            month=request.month,
        ):
            cached = await self._cache.get_monthly_method_success_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_transaction_method_by_merchant_success(
                request
            )
            await self._cache.set_monthly_method_success_by_merchant(request, rows)
            return rows

    async def find_yearly_method_success_by_merchant(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow]:
        with self._obs.span(
            "transaction.stats.find_yearly_method_success_by_merchant",
            merchant_id=request.merchant_id,
            year=request.year,
        ):
            cached = await self._cache.get_yearly_method_success_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_transaction_method_by_merchant_success(
                request
            )
            await self._cache.set_yearly_method_success_by_merchant(request, rows)
            return rows

    async def find_monthly_method_failed_by_merchant(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow]:
        with self._obs.span(
            "transaction.stats.find_monthly_method_failed_by_merchant",
            merchant_id=request.merchant_id,
            year=request.year,
            month=request.month,
        ):
            cached = await self._cache.get_monthly_method_failed_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_transaction_method_by_merchant_failed(
                request
            )
            await self._cache.set_monthly_method_failed_by_merchant(request, rows)
            return rows

    async def find_yearly_method_failed_by_merchant(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow]:
        with self._obs.span(
            "transaction.stats.find_yearly_method_failed_by_merchant",
            merchant_id=request.merchant_id,
            year=request.year,
        ):
            cached = await self._cache.get_yearly_method_failed_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_transaction_method_by_merchant_failed(
                request
            )
            await self._cache.set_yearly_method_failed_by_merchant(request, rows)
            return rows


__all__ = ["TransactionStatsByMerchantServiceImpl"]
