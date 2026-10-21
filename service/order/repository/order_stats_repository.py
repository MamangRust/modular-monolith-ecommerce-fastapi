"""order stats repository. the date arithmetic is reproduced with plain `datetime` helpers: `current_month_start` is the first instant of the requested month, `current_month_end` the last instant, and the previous month is derived the same way. The four timestamps are bound to the verbatim SQL from `pkg/database/query/orders.sql`. Bind adaptations (documented): `$1::type` cast suffixes are rewritten as `CAST(:name AS type)` so SQLAlchemy's `text` does not confuse the `::` with a named bind (same as the category stats SQL). The `EXTRACT`/`TO_CHAR` function calls keep bare `:name` binds, which parse fine."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Protocol

from pkg.database.database import Database
from pkg.database.schema.order import (
    GetMonthlyOrderRow,
    GetMonthlyTotalRevenueRow,
    GetYearlyOrderRow,
    GetYearlyTotalRevenueRow,
)
from shared.domain.requests.order import MonthTotalRevenue
from shared.errors.order_errors import (
    err_get_monthly_order,
    err_get_monthly_total_revenue,
    err_get_yearly_order,
    err_get_yearly_total_revenue,
)

_GET_MONTHLY_TOTAL_REVENUE = """
WITH
    monthly_revenue AS (
        SELECT EXTRACT(
                YEAR
                FROM o.created_at
            )::TEXT AS year, EXTRACT(
                MONTH
                FROM o.created_at
            )::integer AS month, COALESCE(SUM(o.total_price), 0)::INTEGER AS total_revenue
        FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
        WHERE
            o.deleted_at IS NULL
            AND oi.deleted_at IS NULL
            AND (
                (
                    o.created_at >= :extract
                    AND o.created_at <= :created_at
                )
                OR (
                    o.created_at >= :created_at_2
                    AND o.created_at <= :created_at_3
                )
            )
        GROUP BY
            EXTRACT(
                YEAR
                FROM o.created_at
            ),
            EXTRACT(
                MONTH
                FROM o.created_at
            )
    ),
    all_months AS (
        SELECT EXTRACT(
                YEAR
                FROM :extract
            )::TEXT AS year, EXTRACT(
                MONTH
                FROM :extract
            )::integer AS month, TO_CHAR(:extract, 'FMMonth') AS month_name
        UNION
        SELECT EXTRACT(
                YEAR
                FROM :created_at_2
            )::TEXT AS year, EXTRACT(
                MONTH
                FROM :created_at_2
            )::integer AS month, TO_CHAR(:created_at_2, 'FMMonth') AS month_name
    )
SELECT COALESCE(
        am.year, EXTRACT(
            YEAR
            FROM :extract
        )::TEXT
    ) AS year, COALESCE(
        am.month_name, TO_CHAR(:extract, 'FMMonth')
    ) AS month, COALESCE(mr.total_revenue, 0) AS total_revenue
FROM
    all_months am
    LEFT JOIN monthly_revenue mr ON am.year = mr.year
    AND am.month = mr.month
ORDER BY am.year DESC, am.month DESC
"""

_GET_YEARLY_TOTAL_REVENUE = """
WITH
    yearly_revenue AS (
        SELECT EXTRACT(
                YEAR
                FROM o.created_at
            )::integer AS year, COALESCE(SUM(o.total_price), 0)::INTEGER AS total_revenue
        FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
        WHERE
            o.deleted_at IS NULL
            AND oi.deleted_at IS NULL
            AND (
                EXTRACT(
                    YEAR
                    FROM o.created_at
                ) = CAST(:year AS integer)
                OR EXTRACT(
                    YEAR
                    FROM o.created_at
                ) = CAST(:year AS integer) - 1
            )
        GROUP BY
            EXTRACT(
                YEAR
                FROM o.created_at
            )
    ),
    all_years AS (
        SELECT :year AS year
        UNION
        SELECT :year - 1 AS year
    )
SELECT ay.year::text AS year, COALESCE(yr.total_revenue, 0) AS total_revenue
FROM
    all_years ay
    LEFT JOIN yearly_revenue yr ON ay.year = yr.year
ORDER BY ay.year DESC
"""

_GET_MONTHLY_ORDER = """
WITH
    date_range AS (
        SELECT date_trunc('month', CAST(:column1 AS timestamp)) AS start_date, date_trunc('month', CAST(:column1 AS timestamp)) + interval '1 year' - interval '1 day' AS end_date
    ),
    monthly_orders AS (
        SELECT
            date_trunc('month', o.created_at) AS activity_month,
            COUNT(o.order_id) AS order_count,
            SUM(o.total_price)::NUMERIC AS total_revenue,
            SUM(oi.quantity) AS total_items_sold
        FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
        WHERE
            o.deleted_at IS NULL
            AND oi.deleted_at IS NULL
            AND o.created_at BETWEEN (
                SELECT start_date
                FROM date_range
            ) AND (
                SELECT end_date
                FROM date_range
            )
        GROUP BY
            activity_month
    )
SELECT TO_CHAR(mo.activity_month, 'Mon') AS month, mo.order_count, mo.total_revenue, mo.total_items_sold
FROM monthly_orders mo
ORDER BY mo.activity_month
"""

_GET_YEARLY_ORDER = """
WITH
    last_five_years AS (
        SELECT
            EXTRACT(
                YEAR
                FROM o.created_at
            )::text AS year,
            COUNT(o.order_id) AS order_count,
            SUM(o.total_price)::NUMERIC AS total_revenue,
            SUM(oi.quantity) AS total_items_sold,
            COUNT(DISTINCT oi.product_id) AS unique_products_sold
        FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
        WHERE
            o.deleted_at IS NULL
            AND oi.deleted_at IS NULL
            AND EXTRACT(
                YEAR
                FROM o.created_at
            ) BETWEEN (
                EXTRACT(
                    YEAR
                    FROM CAST(:column1 AS timestamp)
                ) - 4
            ) AND EXTRACT(
                YEAR
                FROM CAST(:column1 AS timestamp)
            )
        GROUP BY
            EXTRACT(
                YEAR
                FROM o.created_at
            )
    )
SELECT
    year,
    order_count,
    total_revenue,
    total_items_sold,
    unique_products_sold
FROM last_five_years
ORDER BY year
"""


def _month_start(year: int, month: int) -> datetime:
    return datetime(year, month, 1)


def _next_month_start(start: datetime) -> datetime:
    year = start.year + (1 if start.month == 12 else 0)
    month = 1 if start.month == 12 else start.month + 1
    return datetime(year, month, 1)


def _prev_month_start(start: datetime) -> datetime:
    year = start.year - (1 if start.month == 1 else 0)
    month = 12 if start.month == 1 else start.month - 1
    return datetime(year, month, 1)


class _YearMonth(Protocol):
    """Structural type shared by `MonthTotalRevenue` and its merchant variant."""

    year: int
    month: int


def monthly_revenue_bounds(request: _YearMonth) -> dict[str, datetime]:
    """Compute the four period bounds derives for the monthly queries."""
    current_start = _month_start(request.year, request.month)
    current_end = _next_month_start(current_start) - timedelta(days=1)
    prev_start = _prev_month_start(current_start)
    prev_end = current_start - timedelta(days=1)
    return {
        "extract": current_start,
        "created_at": current_end,
        "created_at_2": prev_start,
        "created_at_3": prev_end,
    }


class OrderStatsRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get_monthly_total_revenue(
        self, request: MonthTotalRevenue
    ) -> list[GetMonthlyTotalRevenueRow]:
        params = dict(monthly_revenue_bounds(request))
        try:
            rows = await self._db.select(_GET_MONTHLY_TOTAL_REVENUE, params)
        except Exception as exc:
            raise err_get_monthly_total_revenue.with_internal(exc) from exc
        return [GetMonthlyTotalRevenueRow.from_row(row) for row in rows]

    async def get_yearly_total_revenue(
        self, year: int
    ) -> list[GetYearlyTotalRevenueRow]:
        try:
            rows = await self._db.select(
                _GET_YEARLY_TOTAL_REVENUE, {"year": year}
            )
        except Exception as exc:
            raise err_get_yearly_total_revenue.with_internal(exc) from exc
        return [GetYearlyTotalRevenueRow.from_row(row) for row in rows]

    async def get_monthly_order(self, year: int) -> list[GetMonthlyOrderRow]:
        params = {"column1": _month_start(year, 1)}
        try:
            rows = await self._db.select(_GET_MONTHLY_ORDER, params)
        except Exception as exc:
            raise err_get_monthly_order.with_internal(exc) from exc
        return [GetMonthlyOrderRow.from_row(row) for row in rows]

    async def get_yearly_order(self, year: int) -> list[GetYearlyOrderRow]:
        params = {"column1": _month_start(year, 1)}
        try:
            rows = await self._db.select(_GET_YEARLY_ORDER, params)
        except Exception as exc:
            raise err_get_yearly_order.with_internal(exc) from exc
        return [GetYearlyOrderRow.from_row(row) for row in rows]


__all__ = ["OrderStatsRepositoryImpl", "monthly_revenue_bounds"]
