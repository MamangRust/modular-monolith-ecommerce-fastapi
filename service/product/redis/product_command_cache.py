"""product command cache invalidation. invalidates the whole `product:*` namespace on every mutation (a product change affects every list projection as well as the detail key), falling back to deleting the by-id key when the pattern invalidation fails. the command service calls this on `Create`, `Update`, `UpdateProductCountStock`, `AdjustProductStock`, `Trash`, `Restore` and `DeletePermanent` (not on the bulk `RestoreAll`/`DeleteAll`)."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.product.redis.common import product_by_id_key
from shared.cache import CacheStore

_PRODUCT_PATTERN = "product:*"


class ProductCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_product(self, product_id: int) -> int:
        deleted = await self._store.invalidate(_PRODUCT_PATTERN)
        if deleted == 0:
            # falls back to the by-id key only when the pattern invalidation
            # errors; `invalidate` swallows errors and returns 0, so a genuine
            # 0-match result also takes this harmless path.
            return await self._store.delete(product_by_id_key(product_id))
        return deleted


__all__ = ["ProductCommandCacheImpl"]
