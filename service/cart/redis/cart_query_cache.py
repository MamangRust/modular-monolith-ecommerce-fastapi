"""cart query cache.

Reads/writes never raise: `CacheStore` swallows Redis errors so a cache outage
degrades to a DB read."""

from __future__ import annotations

from pkg.database.schema.cart import GetCartsRow
from pkg.logger.logger import Logger
from service.cart.redis.cache import decode_page, encode_page
from service.cart.redis.common import TTL_DEFAULT, cart_svc_all_key
from shared.cache import CacheStore
from shared.domain.requests.cart import FindAllCarts


class CartQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_carts(
        self, request: FindAllCarts
    ) -> tuple[list[GetCartsRow], int] | None:
        payload = await self._store.get_json(
            cart_svc_all_key(
                request.user_id, request.page, request.page_size, request.search
            )
        )
        return decode_page(payload)

    async def set_carts(
        self,
        request: FindAllCarts,
        rows: list[GetCartsRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            cart_svc_all_key(
                request.user_id, request.page, request.page_size, request.search
            ),
            encode_page(rows, total),
            TTL_DEFAULT,
        )


__all__ = ["CartQueryCacheImpl"]
