"""cart write repository. `create` maps a missing `RETURNING` row to `err_create_cart` (wraps `sql.ErrNoRows` as `ErrCreateCart`). Both are hard deletes (the cart repository never sets `deleted_at`)."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.cart import CreateCartRow
from shared.domain.requests.cart import (
    CartCreateRecord,
    DeleteAllCartRequest,
    DeleteCartRequest,
)
from shared.errors import (
    err_create_cart,
    err_delete_all_carts,
    err_delete_cart_permanent,
)

_CREATE_CART = """
INSERT INTO carts (
    user_id,
    product_id,
    name,
    price,
    image,
    quantity,
    weight
)
VALUES (
    :user_id,
    :product_id,
    :name,
    :price,
    :image,
    :quantity,
    :weight
)
RETURNING
    cart_id,
    user_id,
    product_id,
    name,
    price,
    image,
    quantity,
    weight,
    created_at,
    updated_at
"""

_DELETE_CART_BY_ID_AND_USER = """
DELETE FROM carts WHERE cart_id = :cart_id AND user_id = :user_id
"""

_DELETE_ALL_CART_BY_USER = """
DELETE FROM carts WHERE cart_id = ANY(:cart_ids) AND user_id = :user_id
"""


class CartCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(self, request: CartCreateRecord) -> CreateCartRow:
        params = {
            "user_id": request.user_id,
            "product_id": request.product_id,
            "name": request.name,
            "price": request.price,
            "image": request.image_product,
            "quantity": request.quantity,
            "weight": request.weight,
        }
        try:
            row = await self._db.execute(_CREATE_CART, params)
        except Exception as exc:
            raise err_create_cart.with_internal(exc) from exc
        if row is None:
            raise err_create_cart
        return CreateCartRow.from_row(row)

    async def delete_permanent(self, request: DeleteCartRequest) -> bool:
        try:
            await self._db.execute(
                _DELETE_CART_BY_ID_AND_USER,
                {"cart_id": request.cart_id, "user_id": request.user_id},
            )
        except Exception as exc:
            raise err_delete_cart_permanent.with_internal(exc) from exc
        return True

    async def delete_all_permanently(self, request: DeleteAllCartRequest) -> bool:
        try:
            await self._db.execute(
                _DELETE_ALL_CART_BY_USER,
                {"cart_ids": request.cart_ids, "user_id": request.user_id},
            )
        except Exception as exc:
            raise err_delete_all_carts.with_internal(exc) from exc
        return True


__all__ = ["CartCommandRepositoryImpl"]
