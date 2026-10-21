"""cart command service. `Create` resolves the product through the gRPC adapter, applies the two business rules inline (`quantity <= 0` → `err_cart_quantity_zero`, `count_in_stock < quantity` → `err_cart_insufficient_stock`), validates the user exists, then writes the cart snapshot (name/price/image/weight copied from the product) and evicts the user's cached listings. No method substitutes a service sentinel."""

from __future__ import annotations

from pkg.database.schema.cart import Cart
from pkg.logger.logger import Logger
from service.cart.redis.interfaces import CartCommandCache
from service.cart.repository.interfaces import (
    CartCommandRepository,
    ProductQueryRepository,
    UserQueryRepository,
)
from shared.domain.requests.cart import (
    CartCreateRecord,
    CreateCartRequest,
    DeleteAllCartRequest,
    DeleteCartRequest,
)
from shared.errors import err_cart_insufficient_stock, err_cart_quantity_zero
from shared.observability import Observability


class CartCommandServiceImpl:
    def __init__(
        self,
        repo: CartCommandRepository,
        product_repo: ProductQueryRepository,
        user_repo: UserQueryRepository,
        cache: CartCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._product_repo = product_repo
        self._user_repo = user_repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(self, request: CreateCartRequest) -> Cart:
        with self._obs.span(
            "cart.command.create",
            product_id=request.product_id,
            user_id=request.user_id,
        ):
            product = await self._product_repo.find_by_id(request.product_id)

            if request.quantity <= 0:
                raise err_cart_quantity_zero
            if product.count_in_stock < request.quantity:
                raise err_cart_insufficient_stock

            await self._user_repo.find_by_id(request.user_id)

            image_product = product.image_product if product.image_product is not None else ""
            weight = product.weight if product.weight is not None else 0

            record = CartCreateRecord(
                product_id=request.product_id,
                user_id=request.user_id,
                name=product.name,
                price=product.price,
                image_product=image_product,
                quantity=request.quantity,
                weight=weight,
            )

            row = await self._repo.create(record)

            await self._cache.delete_cached_carts(request.user_id)

            return Cart(
                cart_id=row.cart_id,
                user_id=row.user_id,
                product_id=row.product_id,
                name=row.name,
                price=row.price,
                image=row.image,
                quantity=row.quantity,
                weight=row.weight,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    async def delete_permanent(self, request: DeleteCartRequest) -> bool:
        with self._obs.span(
            "cart.command.delete_permanent",
            cart_id=request.cart_id,
            user_id=request.user_id,
        ):
            success = await self._repo.delete_permanent(request)
            await self._cache.delete_cached_carts(request.user_id)
            return success

    async def delete_all(self, request: DeleteAllCartRequest) -> bool:
        with self._obs.span(
            "cart.command.delete_all",
            user_id=request.user_id,
        ):
            success = await self._repo.delete_all_permanently(request)
            await self._cache.delete_cached_carts(request.user_id)
            return success


__all__ = ["CartCommandServiceImpl"]
