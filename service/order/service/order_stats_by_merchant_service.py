"""order stats-by-merchant service.

Same cache-first shape as the global stats service; repository errors propagate
unchanged."""

from __future__ import annotations

from pkg.database.schema.order import (
    GetMonthlyOrderRow,
    GetMonthlyTotalRevenueRow,
    GetYearlyOrderRow,
    GetYearlyTotalRevenueRow,
)
from pkg.logger.logger import Logger
from service.order.redis.interfaces import OrderStatsByMerchantCache
from service.order.repository.interfaces import OrderStatsByMerchantRepository
from shared.domain.requests.order import (
    MonthOrderMerchant,
    MonthTotalRevenueMerchant,
    YearOrderMerchant,
    YearTotalRevenueMerchant,
)
from shared.observability import Observability


class OrderStatsByMerchantServiceImpl:
    def __init__(
        self,
        repo: OrderStatsByMerchantRepository,
        cache: OrderStatsByMerchantCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_monthly_total_revenue_by_merchant(
        self, request: MonthTotalRevenueMerchant
    ) -> list[GetMonthlyTotalRevenueRow]:
        with self._obs.span(
            "order.stats.by_merchant.find_monthly_total_revenue",
            merchant_id=request.merchant_id,
            year=request.year,
            month=request.month,
        ):
            cached = await self._cache.get_monthly_total_revenue_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_total_revenue_by_merchant(request)
            await self._cache.set_monthly_total_revenue_by_merchant(request, rows)
            return rows

    async def find_yearly_total_revenue_by_merchant(
        self, request: YearTotalRevenueMerchant
    ) -> list[GetYearlyTotalRevenueRow]:
        with self._obs.span(
            "order.stats.by_merchant.find_yearly_total_revenue",
            merchant_id=request.merchant_id,
            year=request.year,
        ):
            cached = await self._cache.get_yearly_total_revenue_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_total_revenue_by_merchant(request)
            await self._cache.set_yearly_total_revenue_by_merchant(request, rows)
            return rows

    async def find_monthly_order_by_merchant(
        self, request: MonthOrderMerchant
    ) -> list[GetMonthlyOrderRow]:
        with self._obs.span(
            "order.stats.by_merchant.find_monthly_order",
            merchant_id=request.merchant_id,
            year=request.year,
        ):
            cached = await self._cache.get_monthly_order_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_monthly_order_by_merchant(request)
            await self._cache.set_monthly_order_by_merchant(request, rows)
            return rows

    async def find_yearly_order_by_merchant(
        self, request: YearOrderMerchant
    ) -> list[GetYearlyOrderRow]:
        with self._obs.span(
            "order.stats.by_merchant.find_yearly_order",
            merchant_id=request.merchant_id,
            year=request.year,
        ):
            cached = await self._cache.get_yearly_order_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.get_yearly_order_by_merchant(request)
            await self._cache.set_yearly_order_by_merchant(request, rows)
            return rows


__all__ = ["OrderStatsByMerchantServiceImpl"]
