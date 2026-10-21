"""order stats service. Each read is cache-first; a miss loads from the repository and populates the cache. Repository errors propagate unchanged (`HandleError` returns them as-is; the repository already raises `err_get_monthly_total_revenue` etc.)."""

from __future__ import annotations

from pkg.database.schema.order import (
    GetMonthlyOrderRow,
    GetMonthlyTotalRevenueRow,
    GetYearlyOrderRow,
    GetYearlyTotalRevenueRow,
)
from pkg.logger.logger import Logger
from service.order.redis.interfaces import OrderStatsCache
from service.order.repository.interfaces import OrderStatsRepository
from shared.domain.requests.order import MonthTotalRevenue
from shared.observability import Observability


class OrderStatsServiceImpl:
    def __init__(
        self,
        repo: OrderStatsRepository,
        cache: OrderStatsCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_monthly_total_revenue(
        self, request: MonthTotalRevenue
    ) -> list[GetMonthlyTotalRevenueRow]:
        with self._obs.span(
            "order.stats.find_monthly_total_revenue",
            year=request.year,
            month=request.month,
        ):
            cached = await self._cache.get_monthly_total_revenue(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_total_revenue(request)
            await self._cache.set_monthly_total_revenue(request, rows)
            return rows

    async def find_yearly_total_revenue(
        self, year: int
    ) -> list[GetYearlyTotalRevenueRow]:
        with self._obs.span(
            "order.stats.find_yearly_total_revenue", year=year
        ):
            cached = await self._cache.get_yearly_total_revenue(year)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_total_revenue(year)
            await self._cache.set_yearly_total_revenue(year, rows)
            return rows

    async def find_monthly_order(self, year: int) -> list[GetMonthlyOrderRow]:
        with self._obs.span("order.stats.find_monthly_order", year=year):
            cached = await self._cache.get_monthly_order(year)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_order(year)
            await self._cache.set_monthly_order(year, rows)
            return rows

    async def find_yearly_order(self, year: int) -> list[GetYearlyOrderRow]:
        with self._obs.span("order.stats.find_yearly_order", year=year):
            cached = await self._cache.get_yearly_order(year)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_order(year)
            await self._cache.set_yearly_order(year, rows)
            return rows


__all__ = ["OrderStatsServiceImpl"]
