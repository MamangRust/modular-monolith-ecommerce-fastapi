"""Shared SQL templates for the three category stats repositories. the files repeat each query three times, differing only by a trailing `AND c.category_id = $n` / `AND o.merchant_id = $n` predicate before `GROUP BY`; here that predicate is a `{filter}` placeholder rendered per repository so the resulting SQL is textually identical to without triplicating ~700 lines. Bind parameters use `CAST(:name AS type)` instead of `$1::type` suffix (SQLAlchemy's `text` bind parser stops at a following `:`), which also pins the asyncpg parameter type."""

from __future__ import annotations

MONTHLY_TOTAL_PRICE = """
WITH
    monthly_totals AS (
        SELECT
            EXTRACT(YEAR FROM o.created_at)::TEXT AS year,
            EXTRACT(MONTH FROM o.created_at)::integer AS month,
            COALESCE(SUM(o.total_price), 0)::INTEGER AS total_revenue
        FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
        WHERE
            o.deleted_at IS NULL
            AND oi.deleted_at IS NULL
            AND (
                (
                    o.created_at >= CAST(:current_month_start AS timestamp)
                    AND o.created_at <= CAST(:current_month_end AS timestamp)
                )
                OR (
                    o.created_at >= CAST(:prev_month_start AS timestamp)
                    AND o.created_at <= CAST(:prev_month_end AS timestamp)
                )
            )
            {filter}
        GROUP BY
            EXTRACT(YEAR FROM o.created_at),
            EXTRACT(MONTH FROM o.created_at)
    ),
    all_months AS (
        SELECT
            EXTRACT(YEAR FROM CAST(:current_month_start AS timestamp))::TEXT AS year,
            EXTRACT(MONTH FROM CAST(:current_month_start AS timestamp))::integer AS month,
            TO_CHAR(CAST(:current_month_start AS timestamp), 'FMMonth') AS month_name
        UNION
        SELECT
            EXTRACT(YEAR FROM CAST(:prev_month_start AS timestamp))::TEXT AS year,
            EXTRACT(MONTH FROM CAST(:prev_month_start AS timestamp))::integer AS month,
            TO_CHAR(CAST(:prev_month_start AS timestamp), 'FMMonth') AS month_name
    )
SELECT
    COALESCE(
        am.year,
        EXTRACT(YEAR FROM CAST(:current_month_start AS timestamp))::TEXT
    ) AS year,
    COALESCE(
        am.month_name,
        TO_CHAR(CAST(:current_month_start AS timestamp), 'FMMonth')
    ) AS month,
    COALESCE(mt.total_revenue, 0) AS total_revenue
FROM all_months am
    LEFT JOIN monthly_totals mt ON am.year = mt.year AND am.month = mt.month
ORDER BY am.year::INT DESC, am.month DESC
"""

YEARLY_TOTAL_PRICE = """
WITH
    yearly_data AS (
        SELECT
            EXTRACT(YEAR FROM o.created_at)::integer AS year,
            COALESCE(SUM(o.total_price), 0)::INTEGER AS total_revenue
        FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
        WHERE
            o.deleted_at IS NULL
            AND oi.deleted_at IS NULL
            AND p.deleted_at IS NULL
            AND c.deleted_at IS NULL
            AND (
                EXTRACT(YEAR FROM o.created_at) = CAST(:year AS integer)
                OR EXTRACT(YEAR FROM o.created_at) = CAST(:year AS integer) - 1
            )
            {filter}
        GROUP BY
            EXTRACT(YEAR FROM o.created_at)
    ),
    all_years AS (
        SELECT CAST(:year AS integer) AS year
        UNION
        SELECT CAST(:year AS integer) - 1 AS year
    )
SELECT a.year::text AS year, COALESCE(yd.total_revenue, 0) AS total_revenue
FROM all_years a
    LEFT JOIN yearly_data yd ON a.year = yd.year
ORDER BY a.year DESC
"""

MONTHLY_CATEGORY = """
WITH
    date_range AS (
        SELECT
            date_trunc('month', CAST(:year_start AS timestamp)) AS start_date,
            date_trunc('month', CAST(:year_start AS timestamp)) + interval '1 year' - interval '1 day' AS end_date
    ),
    monthly_category_stats AS (
        SELECT
            c.category_id,
            c.name AS category_name,
            date_trunc('month', o.created_at) AS activity_month,
            COUNT(DISTINCT o.order_id) AS order_count,
            SUM(oi.quantity) AS items_sold,
            COALESCE(SUM(o.total_price), 0)::INTEGER AS total_revenue
        FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
        WHERE
            o.deleted_at IS NULL
            AND oi.deleted_at IS NULL
            AND p.deleted_at IS NULL
            AND c.deleted_at IS NULL
            AND o.created_at BETWEEN (
                SELECT start_date FROM date_range
            ) AND (
                SELECT end_date FROM date_range
            )
            {filter}
        GROUP BY
            c.category_id,
            c.name,
            activity_month
    )
SELECT TO_CHAR(mcs.activity_month, 'Mon') AS month, mcs.category_id, mcs.category_name,
       mcs.order_count, mcs.items_sold, mcs.total_revenue
FROM monthly_category_stats mcs
ORDER BY mcs.activity_month, mcs.total_revenue DESC
"""

YEARLY_CATEGORY = """
WITH
    last_five_years AS (
        SELECT
            c.category_id,
            c.name AS category_name,
            EXTRACT(YEAR FROM o.created_at)::text AS year,
            COUNT(DISTINCT o.order_id) AS order_count,
            SUM(oi.quantity) AS items_sold,
            COALESCE(SUM(o.total_price), 0)::INTEGER AS total_revenue,
            COUNT(DISTINCT oi.product_id) AS unique_products_sold
        FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
        WHERE
            o.deleted_at IS NULL
            AND oi.deleted_at IS NULL
            AND p.deleted_at IS NULL
            AND c.deleted_at IS NULL
            AND EXTRACT(YEAR FROM o.created_at) BETWEEN (
                EXTRACT(YEAR FROM CAST(:year_start AS timestamp)) - 4
            ) AND EXTRACT(YEAR FROM CAST(:year_start AS timestamp))
            {filter}
        GROUP BY
            c.category_id,
            c.name,
            EXTRACT(YEAR FROM o.created_at)
    )
SELECT
    year,
    category_id,
    category_name,
    order_count,
    items_sold,
    total_revenue,
    unique_products_sold
FROM last_five_years
ORDER BY year, total_revenue DESC
"""


def render(sql: str, filter_clause: str) -> str:
    """Substitute the repository-specific filter predicate."""
    return sql.replace("{filter}", filter_clause)


__all__ = [
    "MONTHLY_CATEGORY",
    "MONTHLY_TOTAL_PRICE",
    "YEARLY_CATEGORY",
    "YEARLY_TOTAL_PRICE",
    "render",
]
