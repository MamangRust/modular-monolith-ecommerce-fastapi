"""Category stats read repository. Four aggregations over `orders` / `order_items` / `products` / `categories`. The SQL lives in `stats_sql.py`; this module renders it without an extra filter (the base variants). The by-id / by-merchant repositories render the same templates with their own predicate. These queries depend on tables owned by later stages (`orders`, `order_items`, `products`); they only run once those migrations land."""

from __future__ import annotations

from datetime import datetime, timedelta

from pkg.database.database import Database
from pkg.database.schema.category import (
    GetMonthlyCategoryRow,
    GetMonthlyTotalPriceRow,
    GetYearlyCategoryRow,
    GetYearlyTotalPriceRow,
)
from service.category.repository import stats_sql
from shared.errors import (
    err_get_month_price,
    err_get_monthly_total_price,
    err_get_year_price,
    err_get_yearly_total_prices,
)

_NO_FILTER = ""


def _month_bounds(
    year: int, month: int
) -> tuple[datetime, datetime, datetime, datetime]:
    """)."""
    current_month_start = datetime(year, month, 1)
    if month == 12:
        next_month_start = datetime(year + 1, 1, 1)
    else:
        next_month_start = datetime(year, month + 1, 1)
    current_month_end = next_month_start - timedelta(days=1)
    if month == 1:
        prev_month_start = datetime(year - 1, 12, 1)
    else:
        prev_month_start = datetime(year, month - 1, 1)
    prev_month_end = current_month_start - timedelta(days=1)
    return current_month_start, current_month_end, prev_month_start, prev_month_end


class CategoryStatsRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get_monthly_total_price(
        self, year: int, month: int
    ) -> list[GetMonthlyTotalPriceRow]:
        start, end, prev_start, prev_end = _month_bounds(year, month)
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.MONTHLY_TOTAL_PRICE, _NO_FILTER),
                {
                    "current_month_start": start,
                    "current_month_end": end,
                    "prev_month_start": prev_start,
                    "prev_month_end": prev_end,
                },
            )
        except Exception as exc:
            raise err_get_monthly_total_price.with_internal(exc) from exc
        return [GetMonthlyTotalPriceRow.from_row(row) for row in rows]

    async def get_yearly_total_prices(self, year: int) -> list[GetYearlyTotalPriceRow]:
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.YEARLY_TOTAL_PRICE, _NO_FILTER),
                {"year": year},
            )
        except Exception as exc:
            raise err_get_yearly_total_prices.with_internal(exc) from exc
        return [GetYearlyTotalPriceRow.from_row(row) for row in rows]

    async def get_month_price(self, year: int) -> list[GetMonthlyCategoryRow]:
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.MONTHLY_CATEGORY, _NO_FILTER),
                {"year_start": datetime(year, 1, 1)},
            )
        except Exception as exc:
            raise err_get_month_price.with_internal(exc) from exc
        return [GetMonthlyCategoryRow.from_row(row) for row in rows]

    async def get_year_price(self, year: int) -> list[GetYearlyCategoryRow]:
        try:
            rows = await self._db.select(
                stats_sql.render(stats_sql.YEARLY_CATEGORY, _NO_FILTER),
                {"year_start": datetime(year, 1, 1)},
            )
        except Exception as exc:
            raise err_get_year_price.with_internal(exc) from exc
        return [GetYearlyCategoryRow.from_row(row) for row in rows]


__all__ = ["CategoryStatsRepositoryImpl"]
