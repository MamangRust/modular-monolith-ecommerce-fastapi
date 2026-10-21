"""transaction read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page. the `$1::TEXT IS NULL OR...` / `$2::INT IS NULL OR...` search guards are dropped: binds a plain string/int (never nil) and an empty search already matches every row via `ILIKE '%%'` (same normalisation as the order repository). `find_by_id`/`find_by_order_id` map a missing row to `err_transaction_not_found` (404) and any other failure to the per-verb error."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.transaction import (
    GetTransactionByIDRow,
    GetTransactionByMerchantRow,
    GetTransactionByOrderIDRow,
    GetTransactionsActiveRow,
    GetTransactionsRow,
    GetTransactionsTrashedRow,
)
from shared.domain.requests.transaction import (
    FindAllTransaction,
    FindAllTransactionByMerchant,
)
from shared.errors.transaction_errors import (
    err_find_all_transactions,
    err_find_by_active,
    err_find_by_id,
    err_find_by_merchant,
    err_find_by_order_id,
    err_find_by_trashed,
    err_transaction_not_found,
)

_GET_TRANSACTIONS = """
SELECT
    *,
    COUNT(*) OVER() AS total_count
FROM transactions
WHERE deleted_at IS NULL
    AND (
        payment_method ILIKE '%' || :search || '%'
        OR payment_status ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_TRANSACTIONS_ACTIVE = """
SELECT
    *,
    COUNT(*) OVER() AS total_count
FROM transactions
WHERE deleted_at IS NULL
    AND (
        payment_method ILIKE '%' || :search || '%'
        OR payment_status ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_TRANSACTIONS_TRASHED = """
SELECT
    *,
    COUNT(*) OVER() AS total_count
FROM transactions
WHERE deleted_at IS NOT NULL
    AND (
        payment_method ILIKE '%' || :search || '%'
        OR payment_status ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_TRANSACTION_BY_MERCHANT = """
SELECT
    *,
    COUNT(*) OVER() AS total_count
FROM transactions
WHERE deleted_at IS NULL
    AND (
        payment_method ILIKE '%' || :search || '%'
        OR payment_status ILIKE '%' || :search || '%'
    )
    AND merchant_id = :merchant_id
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_TRANSACTION_BY_ORDER_ID = """
SELECT
    transaction_id,
    order_id,
    merchant_id,
    payment_method,
    amount,
    payment_status,
    created_at,
    updated_at
FROM transactions
WHERE order_id = :order_id
    AND deleted_at IS NULL
"""

_GET_TRANSACTION_BY_ID = """
SELECT
    transaction_id,
    order_id,
    merchant_id,
    payment_method,
    amount,
    payment_status,
    created_at,
    updated_at
FROM transactions
WHERE transaction_id = :transaction_id
    AND deleted_at IS NULL
"""


def _page_params(
    request: FindAllTransaction | FindAllTransactionByMerchant,
    **extra: object,
) -> dict[str, object]:
    offset = (request.page - 1) * request.page_size
    return {
        **extra,
        "limit": request.page_size,
        "offset": offset,
    }


class TransactionQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(self, request: FindAllTransaction) -> list[GetTransactionsRow]:
        try:
            rows = await self._db.select(
                _GET_TRANSACTIONS, _page_params(request, search=request.search)
            )
        except Exception as exc:
            raise err_find_all_transactions.with_internal(exc) from exc
        return [GetTransactionsRow.from_row(row) for row in rows]

    async def find_active(
        self, request: FindAllTransaction
    ) -> list[GetTransactionsActiveRow]:
        try:
            rows = await self._db.select(
                _GET_TRANSACTIONS_ACTIVE,
                _page_params(request, search=request.search),
            )
        except Exception as exc:
            raise err_find_by_active.with_internal(exc) from exc
        return [GetTransactionsActiveRow.from_row(row) for row in rows]

    async def find_trashed(
        self, request: FindAllTransaction
    ) -> list[GetTransactionsTrashedRow]:
        try:
            rows = await self._db.select(
                _GET_TRANSACTIONS_TRASHED,
                _page_params(request, search=request.search),
            )
        except Exception as exc:
            raise err_find_by_trashed.with_internal(exc) from exc
        return [GetTransactionsTrashedRow.from_row(row) for row in rows]

    async def find_by_merchant(
        self, request: FindAllTransactionByMerchant
    ) -> list[GetTransactionByMerchantRow]:
        try:
            rows = await self._db.select(
                _GET_TRANSACTION_BY_MERCHANT,
                _page_params(
                    request,
                    search=request.search,
                    merchant_id=request.merchant_id,
                ),
            )
        except Exception as exc:
            raise err_find_by_merchant.with_internal(exc) from exc
        return [GetTransactionByMerchantRow.from_row(row) for row in rows]

    async def find_by_id(self, transaction_id: int) -> GetTransactionByIDRow:
        try:
            row = await self._db.scalar(
                _GET_TRANSACTION_BY_ID, {"transaction_id": transaction_id}
            )
        except Exception as exc:
            raise err_find_by_id.with_internal(exc) from exc
        if row is None:
            raise err_transaction_not_found
        return GetTransactionByIDRow.from_row(row)

    async def find_by_order_id(self, order_id: int) -> GetTransactionByOrderIDRow:
        try:
            row = await self._db.scalar(
                _GET_TRANSACTION_BY_ORDER_ID, {"order_id": order_id}
            )
        except Exception as exc:
            raise err_find_by_order_id.with_internal(exc) from exc
        if row is None:
            raise err_transaction_not_found
        return GetTransactionByOrderIDRow.from_row(row)


__all__ = ["TransactionQueryRepositoryImpl"]
