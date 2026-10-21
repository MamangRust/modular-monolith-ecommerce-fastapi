"""transaction write repository. `update`/`trash`/`restore` map a missing `RETURNING` row to `err_transaction_not_found` (wraps `sql.ErrNoRows`). `create_in_tx` runs the insert inside the caller's `Database.transaction` connection so the business row and its outbox events commit atomically (`CreateInTx(*)`)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text

from pkg.database.database import Database
from pkg.database.schema.transaction import (
    Transaction,
    TransactionRow,
)
from shared.domain.requests.transaction import (
    CreateTransactionRecordRequest,
    UpdateTransactionRecordRequest,
)
from shared.errors.transaction_errors import (
    err_create_transaction,
    err_delete_all_transaction_permanent,
    err_delete_transaction_permanently,
    err_restore_all_transactions,
    err_restore_transaction,
    err_transaction_not_found,
    err_trashed_transaction,
    err_update_transaction,
)

_CREATE_TRANSACTION = """
INSERT INTO transactions (
    order_id, merchant_id, payment_method, amount, payment_status
) VALUES (
    :order_id, :merchant_id, :payment_method, :amount, :payment_status
)
RETURNING
    transaction_id,
    order_id,
    merchant_id,
    payment_method,
    amount,
    payment_status,
    created_at,
    updated_at
"""

_UPDATE_TRANSACTION = """
UPDATE transactions
SET
    merchant_id = :merchant_id,
    payment_method = :payment_method,
    amount = :amount,
    payment_status = :payment_status,
    order_id = :order_id,
    updated_at = CURRENT_TIMESTAMP
WHERE
    transaction_id = :transaction_id
    AND deleted_at IS NULL
RETURNING
    transaction_id,
    order_id,
    merchant_id,
    payment_method,
    amount,
    payment_status,
    created_at,
    updated_at
"""

_TRASH_TRANSACTION = """
UPDATE transactions
SET
    deleted_at = CURRENT_TIMESTAMP
WHERE
    transaction_id = :transaction_id
    AND deleted_at IS NULL
RETURNING
    transaction_id,
    order_id,
    merchant_id,
    payment_method,
    amount,
    payment_status,
    created_at,
    updated_at,
    deleted_at
"""

_RESTORE_TRANSACTION = """
UPDATE transactions
SET
    deleted_at = NULL
WHERE
    transaction_id = :transaction_id
    AND deleted_at IS NOT NULL
RETURNING
    transaction_id,
    order_id,
    merchant_id,
    payment_method,
    amount,
    payment_status,
    created_at,
    updated_at,
    deleted_at
"""

_DELETE_TRANSACTION_PERMANENTLY = """
DELETE FROM transactions WHERE transaction_id = :transaction_id AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_TRANSACTIONS = """
UPDATE transactions
SET
    deleted_at = NULL
WHERE
    deleted_at IS NOT NULL
"""

_DELETE_ALL_PERMANENT_TRANSACTIONS = """
DELETE FROM transactions
WHERE
    deleted_at IS NOT NULL
    OR order_id IN (SELECT order_id FROM orders WHERE deleted_at IS NOT NULL)
"""

_DELETE_TRANSACTION_BY_ORDER_PERMANENT = """
DELETE FROM transactions
WHERE
    order_id = :order_id
"""


class TransactionCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(
        self, request: CreateTransactionRecordRequest
    ) -> TransactionRow:
        params = {
            "order_id": request.order_id,
            "merchant_id": request.merchant_id,
            "payment_method": request.payment_method,
            "amount": request.amount,
            "payment_status": request.payment_status,
        }
        try:
            row = await self._db.execute(_CREATE_TRANSACTION, params)
        except Exception as exc:
            raise err_create_transaction.with_internal(exc) from exc
        if row is None:
            raise err_transaction_not_found
        return TransactionRow.from_row(row)

    async def create_in_tx(
        self, conn: Any, request: CreateTransactionRecordRequest
    ) -> TransactionRow:
        params = {
            "order_id": request.order_id,
            "merchant_id": request.merchant_id,
            "payment_method": request.payment_method,
            "amount": request.amount,
            "payment_status": request.payment_status,
        }
        try:
            result = await conn.execute(text(_CREATE_TRANSACTION), params)
            row = result.mappings().first()
        except Exception as exc:
            raise err_create_transaction.with_internal(exc) from exc
        if row is None:
            raise err_transaction_not_found
        return TransactionRow.from_row(row)

    async def update(
        self, request: UpdateTransactionRecordRequest
    ) -> TransactionRow:
        params = {
            "transaction_id": request.transaction_id,
            "order_id": request.order_id,
            "merchant_id": request.merchant_id,
            "payment_method": request.payment_method,
            "amount": request.amount,
            "payment_status": request.payment_status,
        }
        try:
            row = await self._db.execute(_UPDATE_TRANSACTION, params)
        except Exception as exc:
            raise err_update_transaction.with_internal(exc) from exc
        if row is None:
            raise err_transaction_not_found
        return TransactionRow.from_row(row)

    async def trash(self, transaction_id: int) -> Transaction:
        try:
            row = await self._db.execute(
                _TRASH_TRANSACTION, {"transaction_id": transaction_id}
            )
        except Exception as exc:
            raise err_trashed_transaction.with_internal(exc) from exc
        if row is None:
            raise err_transaction_not_found
        return Transaction.from_row(row)

    async def restore(self, transaction_id: int) -> Transaction:
        try:
            row = await self._db.execute(
                _RESTORE_TRANSACTION, {"transaction_id": transaction_id}
            )
        except Exception as exc:
            raise err_restore_transaction.with_internal(exc) from exc
        if row is None:
            raise err_transaction_not_found
        return Transaction.from_row(row)

    async def delete_permanent(self, transaction_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_TRANSACTION_PERMANENTLY,
                {"transaction_id": transaction_id},
            )
        except Exception as exc:
            raise err_delete_transaction_permanently.with_internal(exc) from exc
        return True

    async def delete_by_order_id_permanent(self, order_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_TRANSACTION_BY_ORDER_PERMANENT, {"order_id": order_id}
            )
        except Exception as exc:
            raise err_delete_transaction_permanently.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_TRANSACTIONS)
        except Exception as exc:
            raise err_restore_all_transactions.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_TRANSACTIONS)
        except Exception as exc:
            raise err_delete_all_transaction_permanent.with_internal(exc) from exc
        return True


__all__ = ["TransactionCommandRepositoryImpl"]
