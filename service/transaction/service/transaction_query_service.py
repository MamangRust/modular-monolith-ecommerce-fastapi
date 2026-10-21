"""transaction query service. Reads are cache-first: a miss loads from the DB and populates the cache with the page and its window `total_count` (taken from the first row; 0 when the page is empty). The service therefore lets repository errors propagate without re-wrapping. NORMALISATION: clamps `page <= 0 → 1` / `pageSize <= 0 → 10` in both the service and the handler; like the other domains, the clamp lives in the gRPC handler (`normalize_page`), so the service receives already-normalised paging."""

from __future__ import annotations

from pkg.database.schema.transaction import (
    GetTransactionByIDRow,
    GetTransactionByOrderIDRow,
    GetTransactionsRow,
)
from pkg.logger.logger import Logger
from service.transaction.redis.interfaces import TransactionQueryCache
from service.transaction.repository.interfaces import TransactionQueryRepository
from shared.domain.requests.transaction import (
    FindAllTransaction,
    FindAllTransactionByMerchant,
)
from shared.observability import Observability


class TransactionQueryServiceImpl:
    def __init__(
        self,
        repo: TransactionQueryRepository,
        cache: TransactionQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int]:
        with self._obs.span(
            "transaction.query.find_all",
            page=request.page,
            page_size=request.page_size,
            search=request.search,
        ):
            cached = await self._cache.get_all(request)
            if cached is not None:
                return cached
            rows = await self._repo.find_all(request)
            total = rows[0].total_count if rows else 0
            await self._cache.set_all(request, rows, total)
            return rows, total

    async def find_by_merchant(
        self, request: FindAllTransactionByMerchant
    ) -> tuple[list[GetTransactionsRow], int]:
        with self._obs.span(
            "transaction.query.find_by_merchant",
            merchant_id=request.merchant_id,
            page=request.page,
            page_size=request.page_size,
            search=request.search,
        ):
            cached = await self._cache.get_by_merchant(request)
            if cached is not None:
                return cached
            rows = await self._repo.find_by_merchant(request)
            total = rows[0].total_count if rows else 0
            await self._cache.set_by_merchant(request, rows, total)
            return rows, total

    async def find_active(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int]:
        with self._obs.span(
            "transaction.query.find_active",
            page=request.page,
            page_size=request.page_size,
        ):
            cached = await self._cache.get_active(request)
            if cached is not None:
                return cached
            rows = await self._repo.find_active(request)
            total = rows[0].total_count if rows else 0
            await self._cache.set_active(request, rows, total)
            return rows, total

    async def find_trashed(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int]:
        with self._obs.span(
            "transaction.query.find_trashed",
            page=request.page,
            page_size=request.page_size,
        ):
            cached = await self._cache.get_trashed(request)
            if cached is not None:
                return cached
            rows = await self._repo.find_trashed(request)
            total = rows[0].total_count if rows else 0
            await self._cache.set_trashed(request, rows, total)
            return rows, total

    async def find_by_id(self, transaction_id: int) -> GetTransactionByIDRow:
        with self._obs.span(
            "transaction.query.find_by_id", transaction_id=transaction_id
        ):
            cached = await self._cache.get_by_id(transaction_id)
            if cached is not None:
                return cached
            row = await self._repo.find_by_id(transaction_id)
            await self._cache.set_by_id(row)
            return row

    async def find_by_order_id(self, order_id: int) -> GetTransactionByOrderIDRow:
        with self._obs.span("transaction.query.find_by_order_id", order_id=order_id):
            cached = await self._cache.get_by_order(order_id)
            if cached is not None:
                return cached
            row = await self._repo.find_by_order_id(order_id)
            await self._cache.set_by_order(order_id, row)
            return row


__all__ = ["TransactionQueryServiceImpl"]
