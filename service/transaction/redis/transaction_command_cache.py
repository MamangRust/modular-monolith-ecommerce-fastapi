"""transaction command cache invalidation. NORMALISATION: `DeleteTransactionCache` invalidates `transaction:*` and, only when that returns an error, falls back to deleting the single `transaction:id:%d` key; `InvalidateTransactionCache` invalidates `transaction:*` and logs on error. The Python `CacheStore.invalidate` swallows Redis errors and returns the deleted-key count, so there is no error branch to take. therefore invalidates the whole `transaction:*` namespace in both methods, matching happy path. The `transaction_id` argument is kept for signature."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.transaction.redis.common import TRANSACTION_NAMESPACE_PATTERN
from shared.cache import CacheStore


class TransactionCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_transaction_cache(self, transaction_id: int) -> int:
        return await self._store.invalidate(TRANSACTION_NAMESPACE_PATTERN)

    async def invalidate_transaction_cache(self) -> int:
        return await self._store.invalidate(TRANSACTION_NAMESPACE_PATTERN)


__all__ = ["TransactionCommandCacheImpl"]
