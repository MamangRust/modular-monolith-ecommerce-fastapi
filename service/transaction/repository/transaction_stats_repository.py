"""transaction stats repository. the date arithmetic is reproduced with plain `datetime` helpers (same precedent as the order stats repository): `current_start` is the first instant of the requested month, `current_end` the last day at 00:00 (`AddDate(0, 1, -1)` truncates the clock — kept verbatim), and the previous month is derived the same way. Bind adaptations (documented): `$1::type` cast suffixes are rewritten as `CAST(:name AS type)` so SQLAlchemy's `text` does not confuse the `::` with a named bind. The SQL text is otherwise verbatim, including the `UNION ALL` zero-filler rows and the `TO_DATE(month, 'Mon')` ordering."""

from __future__ import annotations

from datetime import datetime, timedelta

from pkg.database.database import Database
from pkg.database.schema.transaction import (
    GetMonthlyAmountTransactionFailedRow,
    GetMonthlyAmountTransactionSuccessRow,
    GetMonthlyTransactionMethodsRow,
    GetYearlyAmountTransactionFailedRow,
    GetYearlyAmountTransactionSuccessRow,
    GetYearlyTransactionMethodsRow,
)
from shared.domain.requests.transaction import MonthAmountTransaction, MonthMethodTransaction
from shared.errors.transaction_errors import (
    err_get_monthly_amount_failed,
    err_get_monthly_amount_success,
    err_get_monthly_transaction_method,
    err_get_yearly_amount_failed,
    err_get_yearly_amount_success,
    err_get_yearly_transaction_method,
)

_GET_MONTHLY_AMOUNT_SUCCESS = """
WITH monthly_data AS (
    SELECT
        EXTRACT(YEAR FROM t.created_at)::integer AS year,
        EXTRACT(MONTH FROM t.created_at)::integer AS month,
        COUNT(*) AS total_success,
        COALESCE(SUM(t.amount), 0)::integer AS total_amount
    FROM
        transactions t
    WHERE
        t.deleted_at IS NULL
        AND t.payment_status = 'success'
        AND (
            (t.created_at >= :range1_start AND t.created_at <= :range1_end)
            OR (t.created_at >= :range2_start AND t.created_at <= :range2_end)
        )
    GROUP BY
        EXTRACT(YEAR FROM t.created_at),
        EXTRACT(MONTH FROM t.created_at)
), formatted_data AS (
    SELECT
        year::text,
        TO_CHAR(TO_DATE(month::text, 'MM'), 'Mon') AS month,
        total_success,
        total_amount
    FROM
        monthly_data

    UNION ALL

    SELECT
        EXTRACT(YEAR FROM CAST(:range1_start AS timestamp))::text AS year,
        TO_CHAR(CAST(:range1_start AS timestamp), 'Mon') AS month,
        0 AS total_success,
        0 AS total_amount
    WHERE NOT EXISTS (
        SELECT 1
        FROM monthly_data
        WHERE year = EXTRACT(YEAR FROM CAST(:range1_start AS timestamp))::integer
        AND month = EXTRACT(MONTH FROM CAST(:range1_start AS timestamp))::integer
    )

    UNION ALL

    SELECT
        EXTRACT(YEAR FROM CAST(:range2_start AS timestamp))::text AS year,
        TO_CHAR(CAST(:range2_start AS timestamp), 'Mon') AS month,
        0 AS total_success,
        0 AS total_amount
    WHERE NOT EXISTS (
        SELECT 1
        FROM monthly_data
        WHERE year = EXTRACT(YEAR FROM CAST(:range2_start AS timestamp))::integer
        AND month = EXTRACT(MONTH FROM CAST(:range2_start AS timestamp))::integer
    )
)
SELECT * FROM formatted_data
ORDER BY
    year DESC,
    TO_DATE(month, 'Mon') DESC
"""

_GET_MONTHLY_AMOUNT_FAILED = _GET_MONTHLY_AMOUNT_SUCCESS.replace(
    "COUNT(*) AS total_success", "COUNT(*) AS total_failed"
).replace(
    # the formatted_data branch re-projects the aggregate by name
    "        total_success,\n", "        total_failed,\n"
).replace("t.payment_status = 'success'", "t.payment_status = 'failed'")

_GET_YEARLY_AMOUNT_SUCCESS = """
WITH yearly_data AS (
    SELECT
        EXTRACT(YEAR FROM t.created_at)::integer AS year,
        COUNT(*) AS total_success,
        COALESCE(SUM(t.amount), 0)::integer AS total_amount
    FROM
        transactions t
    WHERE
        t.deleted_at IS NULL
        AND t.payment_status = 'success'
        AND (
            EXTRACT(YEAR FROM t.created_at) = CAST(:year AS integer)
            OR EXTRACT(YEAR FROM t.created_at) = CAST(:year AS integer) - 1
        )
    GROUP BY
        EXTRACT(YEAR FROM t.created_at)
), formatted_data AS (
    SELECT
        year::text,
        total_success::integer,
        total_amount::integer
    FROM
        yearly_data

    UNION ALL

    SELECT
        CAST(:year AS text) AS year,
        0::integer AS total_success,
        0::integer AS total_amount
    WHERE NOT EXISTS (
        SELECT 1
        FROM yearly_data
        WHERE year = CAST(:year AS integer)
    )

    UNION ALL

    SELECT
        (CAST(:year AS integer) - 1)::text AS year,
        0::integer AS total_success,
        0::integer AS total_amount
    WHERE NOT EXISTS (
        SELECT 1
        FROM yearly_data
        WHERE year = CAST(:year AS integer) - 1
    )
)
SELECT * FROM formatted_data
ORDER BY
    year DESC
"""

_GET_YEARLY_AMOUNT_FAILED = _GET_YEARLY_AMOUNT_SUCCESS.replace(
    "COUNT(*) AS total_success", "COUNT(*) AS total_failed"
).replace(
    # the formatted_data branch re-projects the aggregate by name
    "        total_success::integer,", "        total_failed::integer,"
).replace("t.payment_status = 'success'", "t.payment_status = 'failed'")

_GET_MONTHLY_METHOD_SUCCESS = """
WITH
    date_ranges AS (
        SELECT
            CAST(:range1_start AS timestamp) AS range1_start,
            CAST(:range1_end AS timestamp) AS range1_end,
            CAST(:range2_start AS timestamp) AS range2_start,
            CAST(:range2_end AS timestamp) AS range2_end
    ),
    payment_methods AS (
        SELECT DISTINCT
            payment_method
        FROM transactions
        WHERE deleted_at IS NULL
    ),
    all_months AS (
        SELECT generate_series(
            date_trunc('month', LEAST(
                (SELECT range1_start FROM date_ranges),
                (SELECT range2_start FROM date_ranges)
            )),
            date_trunc('month', GREATEST(
                (SELECT range1_end FROM date_ranges),
                (SELECT range2_end FROM date_ranges)
            )),
            interval '1 month'
        )::date AS activity_month
    ),
    all_combinations AS (
        SELECT
            am.activity_month,
            pm.payment_method
        FROM all_months am
        CROSS JOIN payment_methods pm
    ),
    monthly_transactions AS (
        SELECT
            date_trunc('month', t.created_at)::date AS activity_month,
            t.payment_method,
            COUNT(t.transaction_id) AS total_transactions,
            COALESCE(SUM(t.amount), 0)::NUMERIC AS total_amount
        FROM transactions t
        JOIN date_ranges dr ON (
            t.created_at BETWEEN dr.range1_start AND dr.range1_end
            OR t.created_at BETWEEN dr.range2_start AND dr.range2_end
        )
        WHERE
            t.deleted_at IS NULL
            AND t.payment_status = 'success'
        GROUP BY
            date_trunc('month', t.created_at),
            t.payment_method
    )
SELECT
    TO_CHAR(ac.activity_month, 'Mon') AS month,
    ac.payment_method,
    COALESCE(mt.total_transactions, 0) AS total_transactions,
    COALESCE(mt.total_amount, 0) AS total_amount
FROM all_combinations ac
LEFT JOIN monthly_transactions mt ON
    ac.activity_month = mt.activity_month
    AND ac.payment_method = mt.payment_method
ORDER BY
    ac.activity_month,
    ac.payment_method
"""

_GET_MONTHLY_METHOD_FAILED = _GET_MONTHLY_METHOD_SUCCESS.replace(
    "t.payment_status = 'success'", "t.payment_status = 'failed'"
)

_GET_YEARLY_METHOD_SUCCESS = """
WITH
    year_range AS (
        SELECT
            EXTRACT(YEAR FROM CAST(:year_start AS timestamp))::int - 1 AS start_year,
            EXTRACT(YEAR FROM CAST(:year_start AS timestamp))::int AS end_year
    ),
    payment_methods AS (
        SELECT DISTINCT
            payment_method
        FROM transactions
        WHERE deleted_at IS NULL
    ),
    all_years AS (
        SELECT generate_series(
            (SELECT start_year FROM year_range),
            (SELECT end_year FROM year_range)
        )::int AS year
    ),
    all_combinations AS (
        SELECT
            ay.year::text AS year,
            pm.payment_method
        FROM all_years ay
        CROSS JOIN payment_methods pm
    ),
    yearly_transactions AS (
        SELECT
            EXTRACT(YEAR FROM t.created_at)::text AS year,
            t.payment_method,
            COUNT(t.transaction_id) AS total_transactions,
            COALESCE(SUM(t.amount), 0)::NUMERIC AS total_amount
        FROM transactions t
        WHERE
            t.deleted_at IS NULL
            AND t.payment_status = 'success'
            AND EXTRACT(YEAR FROM t.created_at) BETWEEN (SELECT start_year FROM year_range) AND (SELECT end_year FROM year_range)
        GROUP BY
            EXTRACT(YEAR FROM t.created_at),
            t.payment_method
    )
SELECT
    ac.year,
    ac.payment_method,
    COALESCE(yt.total_transactions, 0) AS total_transactions,
    COALESCE(yt.total_amount, 0) AS total_amount
FROM all_combinations ac
LEFT JOIN yearly_transactions yt ON
    ac.year = yt.year
    AND ac.payment_method = yt.payment_method
ORDER BY
    ac.year,
    ac.payment_method
"""

_GET_YEARLY_METHOD_FAILED = _GET_YEARLY_METHOD_SUCCESS.replace(
    "t.payment_status = 'success'", "t.payment_status = 'failed'"
)


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


def monthly_bounds(year: int, month: int) -> dict[str, datetime]:
    """The four period bounds derives for the monthly queries. `range1` covers the requested month, `range2` the previous one. The ends are the last day at 00:00:00 (`AddDate(0, 1, -1)`), kept verbatim."""
    current_start = _month_start(year, month)
    current_end = _next_month_start(current_start) - timedelta(days=1)
    prev_start = _prev_month_start(current_start)
    prev_end = current_start - timedelta(days=1)
    return {
        "range1_start": current_start,
        "range1_end": current_end,
        "range2_start": prev_start,
        "range2_end": prev_end,
    }


class TransactionStatsRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get_monthly_amount_success(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionSuccessRow]:
        try:
            rows = await self._db.select(
                _GET_MONTHLY_AMOUNT_SUCCESS, monthly_bounds(request.year, request.month)
            )
        except Exception as exc:
            raise err_get_monthly_amount_success.with_internal(exc) from exc
        return [GetMonthlyAmountTransactionSuccessRow.from_row(row) for row in rows]

    async def get_yearly_amount_success(
        self, year: int
    ) -> list[GetYearlyAmountTransactionSuccessRow]:
        try:
            rows = await self._db.select(_GET_YEARLY_AMOUNT_SUCCESS, {"year": year})
        except Exception as exc:
            raise err_get_yearly_amount_success.with_internal(exc) from exc
        return [GetYearlyAmountTransactionSuccessRow.from_row(row) for row in rows]

    async def get_monthly_amount_failed(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionFailedRow]:
        try:
            rows = await self._db.select(
                _GET_MONTHLY_AMOUNT_FAILED, monthly_bounds(request.year, request.month)
            )
        except Exception as exc:
            raise err_get_monthly_amount_failed.with_internal(exc) from exc
        return [GetMonthlyAmountTransactionFailedRow.from_row(row) for row in rows]

    async def get_yearly_amount_failed(
        self, year: int
    ) -> list[GetYearlyAmountTransactionFailedRow]:
        try:
            rows = await self._db.select(_GET_YEARLY_AMOUNT_FAILED, {"year": year})
        except Exception as exc:
            raise err_get_yearly_amount_failed.with_internal(exc) from exc
        return [GetYearlyAmountTransactionFailedRow.from_row(row) for row in rows]

    async def get_monthly_transaction_method_success(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow]:
        try:
            rows = await self._db.select(
                _GET_MONTHLY_METHOD_SUCCESS,
                monthly_bounds(request.year, request.month),
            )
        except Exception as exc:
            raise err_get_monthly_transaction_method.with_internal(exc) from exc
        return [GetMonthlyTransactionMethodsRow.from_row(row) for row in rows]

    async def get_yearly_transaction_method_success(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow]:
        params = {"year_start": datetime(year, 1, 1)}
        try:
            rows = await self._db.select(_GET_YEARLY_METHOD_SUCCESS, params)
        except Exception as exc:
            raise err_get_yearly_transaction_method.with_internal(exc) from exc
        return [GetYearlyTransactionMethodsRow.from_row(row) for row in rows]

    async def get_monthly_transaction_method_failed(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow]:
        try:
            rows = await self._db.select(
                _GET_MONTHLY_METHOD_FAILED,
                monthly_bounds(request.year, request.month),
            )
        except Exception as exc:
            raise err_get_monthly_transaction_method.with_internal(exc) from exc
        return [GetMonthlyTransactionMethodsRow.from_row(row) for row in rows]

    async def get_yearly_transaction_method_failed(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow]:
        params = {"year_start": datetime(year, 1, 1)}
        try:
            rows = await self._db.select(_GET_YEARLY_METHOD_FAILED, params)
        except Exception as exc:
            raise err_get_yearly_transaction_method.with_internal(exc) from exc
        return [GetYearlyTransactionMethodsRow.from_row(row) for row in rows]


__all__ = ["TransactionStatsRepositoryImpl", "monthly_bounds"]
