"""order stats-by-merchant repository. Same SQL shapes as the global stats repository with an extra `AND o.merchant_id =:merchant_id` predicate. `$1::type` cast suffixes are rewritten as `CAST(:name AS type)` for SQLAlchemy `text` (see the global stats repository docstring)."""

from __future__ import annotations

from typing import Any

from pkg.database.database import Database
from pkg.database.schema.order import (
    GetMonthlyOrderRow,
    GetMonthlyTotalRevenueRow,
    GetYearlyOrderRow,
    GetYearlyTotalRevenueRow,
)
from service.order.repository.order_stats_repository import (
    _month_start,
    monthly_revenue_bounds,
)
from shared.domain.requests.order import (
    MonthOrderMerchant,
    MonthTotalRevenueMerchant,
    YearOrderMerchant,
    YearTotalRevenueMerchant,
)
from shared.errors.order_errors import (
    err_get_monthly_order_by_merchant,
    err_get_monthly_total_revenue_by_merchant,
    err_get_yearly_order_by_merchant,
    err_get_yearly_total_revenue_by_merchant,
)

_GET_MONTHLY_TOTAL_REVENUE_BY_MERCHANT = """
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
            AND o.merchant_id = :merchant_id
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

_GET_YEARLY_TOTAL_REVENUE_BY_MERCHANT = """
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
            AND o.merchant_id = :merchant_id
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

_GET_MONTHLY_ORDER_BY_MERCHANT = """
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
            AND o.merchant_id = :merchant_id
        GROUP BY
            activity_month
    )
SELECT TO_CHAR(mo.activity_month, 'Mon') AS month, mo.order_count, mo.total_revenue, mo.total_items_sold
FROM monthly_orders mo
ORDER BY mo.activity_month
"""

_GET_YEARLY_ORDER_BY_MERCHANT = """
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
            AND o.merchant_id = :merchant_id
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


class OrderStatsByMerchantRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get_monthly_total_revenue_by_merchant(
        self, request: MonthTotalRevenueMerchant
    ) -> list[GetMonthlyTotalRevenueRow]:
        params: dict[str, Any] = dict(monthly_revenue_bounds(request))
        params["merchant_id"] = request.merchant_id
        try:
            rows = await self._db.select(
                _GET_MONTHLY_TOTAL_REVENUE_BY_MERCHANT, params
            )
        except Exception as exc:
            raise err_get_monthly_total_revenue_by_merchant.with_internal(
                exc
            ) from exc
        return [GetMonthlyTotalRevenueRow.from_row(row) for row in rows]

    async def get_yearly_total_revenue_by_merchant(
        self, request: YearTotalRevenueMerchant
    ) -> list[GetYearlyTotalRevenueRow]:
        params = {"year": request.year, "merchant_id": request.merchant_id}
        try:
            rows = await self._db.select(
                _GET_YEARLY_TOTAL_REVENUE_BY_MERCHANT, params
            )
        except Exception as exc:
            raise err_get_yearly_total_revenue_by_merchant.with_internal(
                exc
            ) from exc
        return [GetYearlyTotalRevenueRow.from_row(row) for row in rows]

    async def get_monthly_order_by_merchant(
        self, request: MonthOrderMerchant
    ) -> list[GetMonthlyOrderRow]:
        params = {
            "column1": _month_start(request.year, 1),
            "merchant_id": request.merchant_id,
        }
        try:
            rows = await self._db.select(_GET_MONTHLY_ORDER_BY_MERCHANT, params)
        except Exception as exc:
            raise err_get_monthly_order_by_merchant.with_internal(exc) from exc
        return [GetMonthlyOrderRow.from_row(row) for row in rows]

    async def get_yearly_order_by_merchant(
        self, request: YearOrderMerchant
    ) -> list[GetYearlyOrderRow]:
        params = {
            "column1": _month_start(request.year, 1),
            "merchant_id": request.merchant_id,
        }
        try:
            rows = await self._db.select(_GET_YEARLY_ORDER_BY_MERCHANT, params)
        except Exception as exc:
            raise err_get_yearly_order_by_merchant.with_internal(exc) from exc
        return [GetYearlyOrderRow.from_row(row) for row in rows]


__all__ = ["OrderStatsByMerchantRepositoryImpl"]
