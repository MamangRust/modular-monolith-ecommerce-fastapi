"""Category stats-by-merchant service."""

from __future__ import annotations

from pkg.database.schema.category import (
    GetMonthlyCategoryByMerchantRow,
    GetMonthlyTotalPriceByMerchantRow,
    GetYearlyCategoryByMerchantRow,
    GetYearlyTotalPriceByMerchantRow,
)
from pkg.logger.logger import Logger
from service.category.redis.interfaces import CategoryStatsByMerchantCache
from service.category.repository.interfaces import CategoryStatsByMerchantRepository
from shared.observability import Observability


class CategoryStatsByMerchantServiceImpl:
    def __init__(
        self,
        repo: CategoryStatsByMerchantRepository,
        cache: CategoryStatsByMerchantCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_monthly_total_price_by_merchant(
        self, year: int, month: int, merchant_id: int
    ) -> list[GetMonthlyTotalPriceByMerchantRow]:
        with self._obs.span(
            "category.stats.find_monthly_total_price_by_merchant",
            year=year,
            month=month,
            merchant_id=merchant_id,
        ):
            cached = await self._cache.get_month_total_price_by_merchant(
                merchant_id, year, month
            )
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_total_price_by_merchant(
                year, month, merchant_id
            )
            await self._cache.set_month_total_price_by_merchant(
                merchant_id, year, month, rows
            )
            return rows

    async def find_yearly_total_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetYearlyTotalPriceByMerchantRow]:
        with self._obs.span(
            "category.stats.find_yearly_total_price_by_merchant",
            year=year,
            merchant_id=merchant_id,
        ):
            cached = await self._cache.get_year_total_price_by_merchant(
                merchant_id, year
            )
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_total_prices_by_merchant(
                year, merchant_id
            )
            await self._cache.set_year_total_price_by_merchant(merchant_id, year, rows)
            return rows

    async def find_month_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetMonthlyCategoryByMerchantRow]:
        with self._obs.span(
            "category.stats.find_month_price_by_merchant",
            year=year,
            merchant_id=merchant_id,
        ):
            cached = await self._cache.get_month_price_by_merchant(merchant_id, year)
            if cached is not None:
                return cached
            rows = await self._repo.get_month_price_by_merchant(year, merchant_id)
            await self._cache.set_month_price_by_merchant(merchant_id, year, rows)
            return rows

    async def find_year_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetYearlyCategoryByMerchantRow]:
        with self._obs.span(
            "category.stats.find_year_price_by_merchant",
            year=year,
            merchant_id=merchant_id,
        ):
            cached = await self._cache.get_year_price_by_merchant(merchant_id, year)
            if cached is not None:
                return cached
            rows = await self._repo.get_year_price_by_merchant(year, merchant_id)
            await self._cache.set_year_price_by_merchant(merchant_id, year, rows)
            return rows


__all__ = ["CategoryStatsByMerchantServiceImpl"]
