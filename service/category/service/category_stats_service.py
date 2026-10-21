"""Category stats service."""

from __future__ import annotations

from pkg.database.schema.category import (
    GetMonthlyCategoryRow,
    GetMonthlyTotalPriceRow,
    GetYearlyCategoryRow,
    GetYearlyTotalPriceRow,
)
from pkg.logger.logger import Logger
from service.category.redis.interfaces import CategoryStatsCache
from service.category.repository.interfaces import CategoryStatsRepository
from shared.observability import Observability


class CategoryStatsServiceImpl:
    def __init__(
        self,
        repo: CategoryStatsRepository,
        cache: CategoryStatsCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_monthly_total_price(
        self, year: int, month: int
    ) -> list[GetMonthlyTotalPriceRow]:
        with self._obs.span(
            "category.stats.find_monthly_total_price", year=year, month=month
        ):
            cached = await self._cache.get_month_total_price(year, month)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_total_price(year, month)
            await self._cache.set_month_total_price(year, month, rows)
            return rows

    async def find_yearly_total_price(self, year: int) -> list[GetYearlyTotalPriceRow]:
        with self._obs.span("category.stats.find_yearly_total_price", year=year):
            cached = await self._cache.get_year_total_price(year)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_total_prices(year)
            await self._cache.set_year_total_price(year, rows)
            return rows

    async def find_month_price(self, year: int) -> list[GetMonthlyCategoryRow]:
        with self._obs.span("category.stats.find_month_price", year=year):
            cached = await self._cache.get_month_price(year)
            if cached is not None:
                return cached
            rows = await self._repo.get_month_price(year)
            await self._cache.set_month_price(year, rows)
            return rows

    async def find_year_price(self, year: int) -> list[GetYearlyCategoryRow]:
        with self._obs.span("category.stats.find_year_price", year=year):
            cached = await self._cache.get_year_price(year)
            if cached is not None:
                return cached
            rows = await self._repo.get_year_price(year)
            await self._cache.set_year_price(year, rows)
            return rows


__all__ = ["CategoryStatsServiceImpl"]
