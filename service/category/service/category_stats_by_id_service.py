"""Category stats-by-id service."""

from __future__ import annotations

from pkg.database.schema.category import (
    GetMonthlyCategoryByIdRow,
    GetMonthlyTotalPriceByIdRow,
    GetYearlyCategoryByIdRow,
    GetYearlyTotalPriceByIdRow,
)
from pkg.logger.logger import Logger
from service.category.redis.interfaces import CategoryStatsByIdCache
from service.category.repository.interfaces import CategoryStatsByIdRepository
from shared.observability import Observability


class CategoryStatsByIdServiceImpl:
    def __init__(
        self,
        repo: CategoryStatsByIdRepository,
        cache: CategoryStatsByIdCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_monthly_total_price_by_id(
        self, year: int, month: int, category_id: int
    ) -> list[GetMonthlyTotalPriceByIdRow]:
        with self._obs.span(
            "category.stats.find_monthly_total_price_by_id",
            year=year,
            month=month,
            category_id=category_id,
        ):
            cached = await self._cache.get_month_total_price_by_id(
                category_id, year, month
            )
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_total_price_by_id(
                year, month, category_id
            )
            await self._cache.set_month_total_price_by_id(
                category_id, year, month, rows
            )
            return rows

    async def find_yearly_total_price_by_id(
        self, year: int, category_id: int
    ) -> list[GetYearlyTotalPriceByIdRow]:
        with self._obs.span(
            "category.stats.find_yearly_total_price_by_id",
            year=year,
            category_id=category_id,
        ):
            cached = await self._cache.get_year_total_price_by_id(category_id, year)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_total_prices_by_id(year, category_id)
            await self._cache.set_year_total_price_by_id(category_id, year, rows)
            return rows

    async def find_month_price_by_id(
        self, year: int, category_id: int
    ) -> list[GetMonthlyCategoryByIdRow]:
        with self._obs.span(
            "category.stats.find_month_price_by_id",
            year=year,
            category_id=category_id,
        ):
            cached = await self._cache.get_month_price_by_id(category_id, year)
            if cached is not None:
                return cached
            rows = await self._repo.get_month_price_by_id(year, category_id)
            await self._cache.set_month_price_by_id(category_id, year, rows)
            return rows

    async def find_year_price_by_id(
        self, year: int, category_id: int
    ) -> list[GetYearlyCategoryByIdRow]:
        with self._obs.span(
            "category.stats.find_year_price_by_id",
            year=year,
            category_id=category_id,
        ):
            cached = await self._cache.get_year_price_by_id(category_id, year)
            if cached is not None:
                return cached
            rows = await self._repo.get_year_price_by_id(year, category_id)
            await self._cache.set_year_price_by_id(category_id, year, rows)
            return rows


__all__ = ["CategoryStatsByIdServiceImpl"]
