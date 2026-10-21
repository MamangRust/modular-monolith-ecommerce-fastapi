"""transaction stats-by-merchant repository. Same shape as the global stats SQL with `AND t.merchant_id =:merchant_id` added to the data CTE. YEAR` (three years) while its data filter covers only `YEAR-1. YEAR`, so the `YEAR-2` row is always a zero row; - the **failed** variant's `year_series` spans `YEAR-1. YEAR`. Bind adaptations mirror the global stats repository (`CAST(:name AS type)`)."""

from __future__ import annotations

from datetime import datetime

from pkg.database.database import Database
from pkg.database.schema.transaction import (
    GetMonthlyAmountTransactionFailedRow,
    GetMonthlyAmountTransactionSuccessRow,
    GetMonthlyTransactionMethodsRow,
    GetYearlyAmountTransactionFailedRow,
    GetYearlyAmountTransactionSuccessRow,
    GetYearlyTransactionMethodsRow,
)
from service.transaction.repository.transaction_stats_repository import (
    _GET_MONTHLY_AMOUNT_SUCCESS,
    _GET_MONTHLY_METHOD_SUCCESS,
    monthly_bounds,
)
from shared.domain.requests.transaction import (
    MonthAmountTransactionMerchant,
    MonthMethodTransactionMerchant,
    YearAmountTransactionMerchant,
    YearMethodTransactionMerchant,
)
from shared.errors.transaction_errors import (
    err_get_monthly_amount_failed_by_merchant,
    err_get_monthly_amount_success_by_merchant,
    err_get_monthly_transaction_method_by_merchant,
    err_get_yearly_amount_failed_by_merchant,
    err_get_yearly_amount_success_by_merchant,
    err_get_yearly_transaction_method_by_merchant,
)

# The by-merchant monthly CTEs are the global ones with the merchant filter
# inserted into the data CTE's WHERE (adds it right after payment_status).
_STATUS_LINE = "        AND t.payment_status = '{status}'\n        AND (\n"
_MERCHANT_LINE = (
    "        AND t.payment_status = '{status}'\n"
    "        AND t.merchant_id = :merchant_id\n"
    "        AND (\n"
)

_GET_MONTHLY_AMOUNT_SUCCESS_BY_MERCHANT = _GET_MONTHLY_AMOUNT_SUCCESS.replace(
    _STATUS_LINE.format(status="success"), _MERCHANT_LINE.format(status="success")
)
_GET_MONTHLY_AMOUNT_FAILED_BY_MERCHANT = _GET_MONTHLY_AMOUNT_SUCCESS_BY_MERCHANT.replace(
    "COUNT(*) AS total_success", "COUNT(*) AS total_failed"
).replace(
    # the formatted_data branch re-projects the aggregate by name
    "        total_success,\n", "        total_failed,\n"
).replace("t.payment_status = 'success'", "t.payment_status = 'failed'")

_GET_MONTHLY_METHOD_SUCCESS_BY_MERCHANT = _GET_MONTHLY_METHOD_SUCCESS.replace(
    "            t.deleted_at IS NULL\n            AND t.payment_status = 'success'\n        GROUP BY",
    "            t.deleted_at IS NULL\n            AND t.payment_status = 'success'\n            AND t.merchant_id = :merchant_id\n        GROUP BY",
)
_GET_MONTHLY_METHOD_FAILED_BY_MERCHANT = _GET_MONTHLY_METHOD_SUCCESS_BY_MERCHANT.replace(
    "t.payment_status = 'success'", "t.payment_status = 'failed'"
)


def _yearly_amount_by_merchant(status: str, aggregate: str) -> str:
    return f"""
WITH yearly_data AS (
    SELECT
        EXTRACT(YEAR FROM t.created_at)::integer AS year,
        COUNT(*) AS {aggregate},
        COALESCE(SUM(t.amount), 0)::integer AS total_amount
    FROM
        transactions t
    WHERE
        t.deleted_at IS NULL
        AND t.payment_status = '{status}'
        AND t.merchant_id = :merchant_id
        AND (
            EXTRACT(YEAR FROM t.created_at) = CAST(:year AS integer)
            OR EXTRACT(YEAR FROM t.created_at) = CAST(:year AS integer) - 1
        )
    GROUP BY
        EXTRACT(YEAR FROM t.created_at)
), formatted_data AS (
    SELECT
        year::text,
        {aggregate}::integer,
        total_amount::integer
    FROM
        yearly_data

    UNION ALL

    SELECT
        CAST(:year AS text) AS year,
        0::integer AS {aggregate},
        0::integer AS total_amount
    WHERE NOT EXISTS (
        SELECT 1
        FROM yearly_data
        WHERE year = CAST(:year AS integer)
    )

    UNION ALL

    SELECT
        (CAST(:year AS integer) - 1)::text AS year,
        0::integer AS {aggregate},
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


_GET_YEARLY_AMOUNT_SUCCESS_BY_MERCHANT = _yearly_amount_by_merchant(
    "success", "total_success"
)
_GET_YEARLY_AMOUNT_FAILED_BY_MERCHANT = _yearly_amount_by_merchant(
    "failed", "total_failed"
)


def _yearly_method_by_merchant(status: str, series_offset: int) -> str:
    return f"""
WITH
    year_series AS (
        SELECT generate_series(
            EXTRACT(YEAR FROM CAST(:year_start AS timestamp))::integer - {series_offset},
            EXTRACT(YEAR FROM CAST(:year_start AS timestamp))::integer,
            1
        ) AS year
    ),
    yearly_transactions AS (
        SELECT
            EXTRACT(YEAR FROM t.created_at)::integer AS year,
            t.payment_method,
            COUNT(t.transaction_id) AS total_transactions,
            SUM(t.amount)::NUMERIC AS total_amount
        FROM transactions t
        WHERE
            t.deleted_at IS NULL
            AND t.payment_status = '{status}'
            AND t.merchant_id = :merchant_id
            AND EXTRACT(YEAR FROM t.created_at) BETWEEN (EXTRACT(YEAR FROM CAST(:year_start AS timestamp)) - 1) AND EXTRACT(YEAR FROM CAST(:year_start AS timestamp))
        GROUP BY
            year,
            t.payment_method
    ),
    payment_methods AS (
        SELECT DISTINCT payment_method
        FROM transactions
        WHERE deleted_at IS NULL
    )
SELECT
    ys.year::text AS year,
    pm.payment_method,
    COALESCE(yt.total_transactions, 0) AS total_transactions,
    COALESCE(yt.total_amount, 0) AS total_amount
FROM year_series ys
CROSS JOIN payment_methods pm
LEFT JOIN yearly_transactions yt
    ON ys.year = yt.year
    AND pm.payment_method = yt.payment_method
ORDER BY ys.year, pm.payment_method
"""


# data filter covers YEAR-1 .. YEAR — the YEAR-2 row is always zeros.
_GET_YEARLY_METHOD_SUCCESS_BY_MERCHANT = _yearly_method_by_merchant("success", 2)
_GET_YEARLY_METHOD_FAILED_BY_MERCHANT = _yearly_method_by_merchant("failed", 1)


class TransactionStatsByMerchantRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get_monthly_amount_success_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionSuccessRow]:
        params = {
            **monthly_bounds(request.year, request.month),
            "merchant_id": request.merchant_id,
        }
        try:
            rows = await self._db.select(
                _GET_MONTHLY_AMOUNT_SUCCESS_BY_MERCHANT, params
            )
        except Exception as exc:
            raise err_get_monthly_amount_success_by_merchant.with_internal(exc) from exc
        return [GetMonthlyAmountTransactionSuccessRow.from_row(row) for row in rows]

    async def get_yearly_amount_success_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionSuccessRow]:
        params = {"year": request.year, "merchant_id": request.merchant_id}
        try:
            rows = await self._db.select(
                _GET_YEARLY_AMOUNT_SUCCESS_BY_MERCHANT, params
            )
        except Exception as exc:
            raise err_get_yearly_amount_success_by_merchant.with_internal(exc) from exc
        return [GetYearlyAmountTransactionSuccessRow.from_row(row) for row in rows]

    async def get_monthly_amount_failed_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionFailedRow]:
        params = {
            **monthly_bounds(request.year, request.month),
            "merchant_id": request.merchant_id,
        }
        try:
            rows = await self._db.select(
                _GET_MONTHLY_AMOUNT_FAILED_BY_MERCHANT, params
            )
        except Exception as exc:
            raise err_get_monthly_amount_failed_by_merchant.with_internal(exc) from exc
        return [GetMonthlyAmountTransactionFailedRow.from_row(row) for row in rows]

    async def get_yearly_amount_failed_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionFailedRow]:
        params = {"year": request.year, "merchant_id": request.merchant_id}
        try:
            rows = await self._db.select(
                _GET_YEARLY_AMOUNT_FAILED_BY_MERCHANT, params
            )
        except Exception as exc:
            raise err_get_yearly_amount_failed_by_merchant.with_internal(exc) from exc
        return [GetYearlyAmountTransactionFailedRow.from_row(row) for row in rows]

    async def get_monthly_transaction_method_by_merchant_success(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow]:
        params = {
            **monthly_bounds(request.year, request.month),
            "merchant_id": request.merchant_id,
        }
        try:
            rows = await self._db.select(
                _GET_MONTHLY_METHOD_SUCCESS_BY_MERCHANT, params
            )
        except Exception as exc:
            raise err_get_monthly_transaction_method_by_merchant.with_internal(exc) from exc
        return [GetMonthlyTransactionMethodsRow.from_row(row) for row in rows]

    async def get_yearly_transaction_method_by_merchant_success(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow]:
        params = {
            "year_start": datetime(request.year, 1, 1),
            "merchant_id": request.merchant_id,
        }
        try:
            rows = await self._db.select(
                _GET_YEARLY_METHOD_SUCCESS_BY_MERCHANT, params
            )
        except Exception as exc:
            raise err_get_yearly_transaction_method_by_merchant.with_internal(exc) from exc
        return [GetYearlyTransactionMethodsRow.from_row(row) for row in rows]

    async def get_monthly_transaction_method_by_merchant_failed(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow]:
        params = {
            **monthly_bounds(request.year, request.month),
            "merchant_id": request.merchant_id,
        }
        try:
            rows = await self._db.select(
                _GET_MONTHLY_METHOD_FAILED_BY_MERCHANT, params
            )
        except Exception as exc:
            raise err_get_monthly_transaction_method_by_merchant.with_internal(exc) from exc
        return [GetMonthlyTransactionMethodsRow.from_row(row) for row in rows]

    async def get_yearly_transaction_method_by_merchant_failed(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow]:
        params = {
            "year_start": datetime(request.year, 1, 1),
            "merchant_id": request.merchant_id,
        }
        try:
            rows = await self._db.select(
                _GET_YEARLY_METHOD_FAILED_BY_MERCHANT, params
            )
        except Exception as exc:
            raise err_get_yearly_transaction_method_by_merchant.with_internal(exc) from exc
        return [GetYearlyTransactionMethodsRow.from_row(row) for row in rows]


__all__ = ["TransactionStatsByMerchantRepositoryImpl"]
