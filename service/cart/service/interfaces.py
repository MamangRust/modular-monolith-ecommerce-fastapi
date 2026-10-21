"""cart service"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.cart import Cart, GetCartsRow
from shared.domain.requests.cart import (
    CreateCartRequest,
    DeleteAllCartRequest,
    DeleteCartRequest,
    FindAllCarts,
)


class CartQueryService(Protocol):
    async def find_all(self, request: FindAllCarts) -> tuple[list[GetCartsRow], int]: ...


class CartCommandService(Protocol):
    async def create(self, request: CreateCartRequest) -> Cart: ...

    async def delete_permanent(self, request: DeleteCartRequest) -> bool: ...

    async def delete_all(self, request: DeleteAllCartRequest) -> bool: ...


__all__ = [
    "CartCommandService",
    "CartQueryService",
]
