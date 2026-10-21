"""transaction query cache.

Reads/writes never raise: `CacheStore` swallows Redis errors so a cache outage
degrades to a DB read. Each list page stores `{data, total_records}`; the
by-id/by-order entries store the row directly."""

from __future__ import annotations

from typing import Any

from pkg.database.schema.transaction import (
    GetTransactionByIDRow,
    GetTransactionByOrderIDRow,
    GetTransactionsRow,
)
from pkg.logger.logger import Logger
from service.transaction.redis.cache import (
    transaction_by_id_from_dict,
    transaction_by_id_to_dict,
    transaction_by_order_from_dict,
    transaction_by_order_to_dict,
    transactions_row_from_dict,
    transactions_row_to_dict,
)
from service.transaction.redis.common import (
    TTL_DEFAULT,
    transaction_active_key,
    transaction_all_key,
    transaction_by_id_key,
    transaction_by_merchant_key,
    transaction_by_order_key,
    transaction_trashed_key,
)
from shared.cache import CacheStore
from shared.domain.requests.transaction import (
    FindAllTransaction,
    FindAllTransactionByMerchant,
)


def _encode(
    rows: list[GetTransactionsRow], total: int
) -> dict[str, Any]:
    return {
        "data": [transactions_row_to_dict(row) for row in rows],
        "total_records": total,
    }


def _decode(payload: Any) -> tuple[list[GetTransactionsRow], int] | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    total = int(payload.get("total_records") or 0)
    return [transactions_row_from_dict(item, total) for item in data], total


class TransactionQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    # ---- FindAll ----

    async def get_all(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int] | None:
        payload = await self._store.get_json(
            transaction_all_key(request.page, request.page_size, request.search)
        )
        return _decode(payload)

    async def set_all(
        self, request: FindAllTransaction, rows: list[GetTransactionsRow], total: int
    ) -> None:
        await self._store.set_json(
            transaction_all_key(request.page, request.page_size, request.search),
            _encode(rows, total),
            TTL_DEFAULT,
        )

    # ---- FindByMerchant ----

    async def get_by_merchant(
        self, request: FindAllTransactionByMerchant
    ) -> tuple[list[GetTransactionsRow], int] | None:
        payload = await self._store.get_json(
            transaction_by_merchant_key(
                request.merchant_id, request.page, request.page_size, request.search
            )
        )
        return _decode(payload)

    async def set_by_merchant(
        self,
        request: FindAllTransactionByMerchant,
        rows: list[GetTransactionsRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            transaction_by_merchant_key(
                request.merchant_id, request.page, request.page_size, request.search
            ),
            _encode(rows, total),
            TTL_DEFAULT,
        )

    # ---- FindByActive ----

    async def get_active(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int] | None:
        payload = await self._store.get_json(
            transaction_active_key(request.page, request.page_size, request.search)
        )
        return _decode(payload)

    async def set_active(
        self, request: FindAllTransaction, rows: list[GetTransactionsRow], total: int
    ) -> None:
        await self._store.set_json(
            transaction_active_key(request.page, request.page_size, request.search),
            _encode(rows, total),
            TTL_DEFAULT,
        )

    # ---- FindByTrashed ----

    async def get_trashed(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int] | None:
        payload = await self._store.get_json(
            transaction_trashed_key(request.page, request.page_size, request.search)
        )
        return _decode(payload)

    async def set_trashed(
        self, request: FindAllTransaction, rows: list[GetTransactionsRow], total: int
    ) -> None:
        await self._store.set_json(
            transaction_trashed_key(request.page, request.page_size, request.search),
            _encode(rows, total),
            TTL_DEFAULT,
        )

    # ---- FindById ----

    async def get_by_id(self, transaction_id: int) -> GetTransactionByIDRow | None:
        payload = await self._store.get_json(transaction_by_id_key(transaction_id))
        if not isinstance(payload, dict):
            return None
        try:
            return transaction_by_id_from_dict(payload)
        except (KeyError, TypeError, ValueError) as exc:
            self._logger.error(
                "corrupt transaction cache payload dropped", error=str(exc)
            )
            return None

    async def set_by_id(self, row: GetTransactionByIDRow) -> None:
        await self._store.set_json(
            transaction_by_id_key(row.transaction_id),
            transaction_by_id_to_dict(row),
            TTL_DEFAULT,
        )

    # ---- FindByOrderId ----

    async def get_by_order(self, order_id: int) -> GetTransactionByOrderIDRow | None:
        payload = await self._store.get_json(transaction_by_order_key(order_id))
        if not isinstance(payload, dict):
            return None
        try:
            return transaction_by_order_from_dict(payload)
        except (KeyError, TypeError, ValueError) as exc:
            self._logger.error(
                "corrupt transaction cache payload dropped", error=str(exc)
            )
            return None

    async def set_by_order(
        self, order_id: int, row: GetTransactionByOrderIDRow
    ) -> None:
        await self._store.set_json(
            transaction_by_order_key(order_id),
            transaction_by_order_to_dict(row),
            TTL_DEFAULT,
        )


__all__ = ["TransactionQueryCacheImpl"]
