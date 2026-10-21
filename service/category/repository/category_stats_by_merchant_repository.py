"""Category stats-by-merchant read repository.

Same templates as the base stats repository, rendered with
`AND o.merchant_id = CAST(:merchant_id AS integer)`."""

from __future__ import annotations

from datetime import datetime

from pkg.database.database import Database
from pkg.database.schema.category import (
    GetMonthlyCategoryByMerchantRow,
    GetMonthlyTotalPriceByMerchantRow,
    GetYearlyCategoryByMerchantRow,
    GetYearlyTotalPriceByMerchantRow,
)
from service.category.repository import stats_sql
from service.category.repository.category_stats_repository import _month_bounds
from shared.errors import (
    err_get_month_price_by_merchant,
    err_get_monthly_total_price_by_merchant,
    err_get_year_price_by_merchant,
    err_get_yearly_total_prices_by_merchant,
)

_FILTER = "AND o.merchant_id = CAST(:merchant_id AS integer)"


class CategoryStatsByMerchantRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get_monthly_total_price_by_merchant(
        self, year: int, month: int, merchant_id: int
    ) -> list[GetMonthlyTotalPriceByMerchantRow]:
        start, end, prev_start, prev_end = _month_bounds(year, month)
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.MONTHLY_TOTAL_PRICE, _FILTER),
                {
                    "current_month_start": start,
                    "current_month_end": end,
                    "prev_month_start": prev_start,
                    "prev_month_end": prev_end,
                    "merchant_id": merchant_id,
                },
            )
        except Exception as exc:
            raise err_get_monthly_total_price_by_merchant.with_internal(exc) from exc
        return [GetMonthlyTotalPriceByMerchantRow.from_row(row) for row in rows]

    async def get_yearly_total_prices_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetYearlyTotalPriceByMerchantRow]:
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.YEARLY_TOTAL_PRICE, _FILTER),
                {"year": year, "merchant_id": merchant_id},
            )
        except Exception as exc:
            raise err_get_yearly_total_prices_by_merchant.with_internal(exc) from exc
        return [GetYearlyTotalPriceByMerchantRow.from_row(row) for row in rows]

    async def get_month_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetMonthlyCategoryByMerchantRow]:
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.MONTHLY_CATEGORY, _FILTER),
                {"year_start": datetime(year, 1, 1), "merchant_id": merchant_id},
            )
        except Exception as exc:
            raise err_get_month_price_by_merchant.with_internal(exc) from exc
        return [GetMonthlyCategoryByMerchantRow.from_row(row) for row in rows]

    async def get_year_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetYearlyCategoryByMerchantRow]:
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.YEARLY_CATEGORY, _FILTER),
                {"year_start": datetime(year, 1, 1), "merchant_id": merchant_id},
            )
        except Exception as exc:
            raise err_get_year_price_by_merchant.with_internal(exc) from exc
        return [GetYearlyCategoryByMerchantRow.from_row(row) for row in rows]


__all__ = ["CategoryStatsByMerchantRepositoryImpl"]
