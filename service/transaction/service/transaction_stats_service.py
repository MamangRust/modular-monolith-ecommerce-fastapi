"""transaction stats service. Pure cache → repository fan-out; stats services have **no** year/month validation (the catalogue's `ErrGrpcInvalidYear`/`ErrGrpcInvalidMonth` are unreferenced), so neither does."""

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
from service.transaction.redis.interfaces import TransactionStatsCache
from service.transaction.repository.interfaces import TransactionStatsRepository
from shared.domain.requests.transaction import MonthAmountTransaction, MonthMethodTransaction
from shared.observability import Observability


class TransactionStatsServiceImpl:
    def __init__(
        self,
        repo: TransactionStatsRepository,
        cache: TransactionStatsCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_monthly_amount_success(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionSuccessRow]:
        with self._obs.span(
            "transaction.stats.find_monthly_amount_success",
            year=request.year,
            month=request.month,
        ):
            cached = await self._cache.get_monthly_amount_success(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_amount_success(request)
            await self._cache.set_monthly_amount_success(request, rows)
            return rows

    async def find_yearly_amount_success(
        self, year: int
    ) -> list[GetYearlyAmountTransactionSuccessRow]:
        with self._obs.span(
            "transaction.stats.find_yearly_amount_success", year=year
        ):
            cached = await self._cache.get_yearly_amount_success(year)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_amount_success(year)
            await self._cache.set_yearly_amount_success(year, rows)
            return rows

    async def find_monthly_amount_failed(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionFailedRow]:
        with self._obs.span(
            "transaction.stats.find_monthly_amount_failed",
            year=request.year,
            month=request.month,
        ):
            cached = await self._cache.get_monthly_amount_failed(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_amount_failed(request)
            await self._cache.set_monthly_amount_failed(request, rows)
            return rows

    async def find_yearly_amount_failed(
        self, year: int
    ) -> list[GetYearlyAmountTransactionFailedRow]:
        with self._obs.span(
            "transaction.stats.find_yearly_amount_failed", year=year
        ):
            cached = await self._cache.get_yearly_amount_failed(year)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_amount_failed(year)
            await self._cache.set_yearly_amount_failed(year, rows)
            return rows

    async def find_monthly_method_success(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow]:
        with self._obs.span(
            "transaction.stats.find_monthly_method_success",
            year=request.year,
            month=request.month,
        ):
            cached = await self._cache.get_monthly_method_success(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_transaction_method_success(request)
            await self._cache.set_monthly_method_success(request, rows)
            return rows

    async def find_yearly_method_success(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow]:
        with self._obs.span(
            "transaction.stats.find_yearly_method_success", year=year
        ):
            cached = await self._cache.get_yearly_method_success(year)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_transaction_method_success(year)
            await self._cache.set_yearly_method_success(year, rows)
            return rows

    async def find_monthly_method_failed(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow]:
        with self._obs.span(
            "transaction.stats.find_monthly_method_failed",
            year=request.year,
            month=request.month,
        ):
            cached = await self._cache.get_monthly_method_failed(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_transaction_method_failed(request)
            await self._cache.set_monthly_method_failed(request, rows)
            return rows

    async def find_yearly_method_failed(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow]:
        with self._obs.span(
            "transaction.stats.find_yearly_method_failed", year=year
        ):
            cached = await self._cache.get_yearly_method_failed(year)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_transaction_method_failed(year)
            await self._cache.set_yearly_method_failed(year, rows)
            return rows


__all__ = ["TransactionStatsServiceImpl"]
