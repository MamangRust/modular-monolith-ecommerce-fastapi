"""The other two repositories are SQL-backed. Both adapters are consumed by the command service's `Create` (product details + user existence)."""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.cart import CreateCartRow, GetCartsRow
from pkg.database.schema.product import GetProductByIDRow
from pkg.database.schema.user import GetUserByIDRow
from shared.domain.requests.cart import (
    CartCreateRecord,
    DeleteAllCartRequest,
    DeleteCartRequest,
    FindAllCarts,
)


class ProductQueryRepository(Protocol):
    async def find_by_id(self, product_id: int) -> GetProductByIDRow: ...


class UserQueryRepository(Protocol):
    async def find_by_id(self, user_id: int) -> GetUserByIDRow: ...


class CartQueryRepository(Protocol):
    async def find_all(self, request: FindAllCarts) -> list[GetCartsRow]: ...


class CartCommandRepository(Protocol):
    async def create(self, request: CartCreateRecord) -> CreateCartRow: ...

    async def delete_permanent(self, request: DeleteCartRequest) -> bool: ...

    async def delete_all_permanently(self, request: DeleteAllCartRequest) -> bool: ...


__all__ = [
    "CartCommandRepository",
    "CartQueryRepository",
    "ProductQueryRepository",
    "UserQueryRepository",
]
