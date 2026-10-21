"""Category stats-by-id read repository.

Same templates as the base stats repository, rendered with
`AND c.category_id = CAST(:category_id AS integer)`."""

from __future__ import annotations

from datetime import datetime

from pkg.database.database import Database
from pkg.database.schema.category import (
    GetMonthlyCategoryByIdRow,
    GetMonthlyTotalPriceByIdRow,
    GetYearlyCategoryByIdRow,
    GetYearlyTotalPriceByIdRow,
)
from service.category.repository import stats_sql
from service.category.repository.category_stats_repository import _month_bounds
from shared.errors import (
    err_get_month_price_by_id,
    err_get_monthly_total_price_by_id,
    err_get_year_price_by_id,
    err_get_yearly_total_prices_by_id,
)

_FILTER = "AND c.category_id = CAST(:category_id AS integer)"


class CategoryStatsByIdRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get_monthly_total_price_by_id(
        self, year: int, month: int, category_id: int
    ) -> list[GetMonthlyTotalPriceByIdRow]:
        start, end, prev_start, prev_end = _month_bounds(year, month)
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.MONTHLY_TOTAL_PRICE, _FILTER),
                {
                    "current_month_start": start,
                    "current_month_end": end,
                    "prev_month_start": prev_start,
                    "prev_month_end": prev_end,
                    "category_id": category_id,
                },
            )
        except Exception as exc:
            raise err_get_monthly_total_price_by_id.with_internal(exc) from exc
        return [GetMonthlyTotalPriceByIdRow.from_row(row) for row in rows]

    async def get_yearly_total_prices_by_id(
        self, year: int, category_id: int
    ) -> list[GetYearlyTotalPriceByIdRow]:
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.YEARLY_TOTAL_PRICE, _FILTER),
                {"year": year, "category_id": category_id},
            )
        except Exception as exc:
            raise err_get_yearly_total_prices_by_id.with_internal(exc) from exc
        return [GetYearlyTotalPriceByIdRow.from_row(row) for row in rows]

    async def get_month_price_by_id(
        self, year: int, category_id: int
    ) -> list[GetMonthlyCategoryByIdRow]:
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.MONTHLY_CATEGORY, _FILTER),
                {"year_start": datetime(year, 1, 1), "category_id": category_id},
            )
        except Exception as exc:
            raise err_get_month_price_by_id.with_internal(exc) from exc
        return [GetMonthlyCategoryByIdRow.from_row(row) for row in rows]

    async def get_year_price_by_id(
        self, year: int, category_id: int
    ) -> list[GetYearlyCategoryByIdRow]:
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.YEARLY_CATEGORY, _FILTER),
                {"year_start": datetime(year, 1, 1), "category_id": category_id},
            )
        except Exception as exc:
            raise err_get_year_price_by_id.with_internal(exc) from exc
        return [GetYearlyCategoryByIdRow.from_row(row) for row in rows]


__all__ = ["CategoryStatsByIdRepositoryImpl"]
