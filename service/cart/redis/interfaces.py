"""cart cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.cart import GetCartsRow
from shared.domain.requests.cart import FindAllCarts


class CartQueryCache(Protocol):
    async def get_carts(
        self, request: FindAllCarts
    ) -> tuple[list[GetCartsRow], int] | None: ...

    async def set_carts(
        self,
        request: FindAllCarts,
        rows: list[GetCartsRow],
        total: int,
    ) -> None: ...


class CartCommandCache(Protocol):
    async def delete_cached_carts(self, user_id: int) -> int: ...


__all__ = [
    "CartCommandCache",
    "CartQueryCache",
]
