"""product command service. `Create`/`Update` validate the parent category and merchant through the gRPC adapters before writing, then derive `slug_product` with `generate_slug`. Only three methods substitute a service sentinel: - `update_product_count_stock`: guard `product_id <= 0 || stock < 0` → `err_failed_count_stock`; - `adjust_product_stock`: guard `product_id <= 0 || delta == 0 || operation_id == ""` → `err_failed_count_stock`; - `delete_all`: any repository failure → `err_failed_delete_all_products_permanent`. `delete_permanent` loads the trashed row first so it can remove the stored image from disk (`os.remove`), ignoring a missing file, before deleting the row; a real removal failure surfaces as `err_failed_delete_image_product`."""

from __future__ import annotations

import os

from pkg.database.schema.product import (
    AdjustProductStockRow,
    CreateProductRow,
    Product,
    UpdateProductCountStockRow,
    UpdateProductRow,
)
from pkg.logger.logger import Logger
from pkg.utils.slug import generate_slug
from service.product.redis.interfaces import ProductCommandCache
from service.product.repository.interfaces import (
    CategoryQueryRepository,
    MerchantQueryRepository,
    ProductCommandRepository,
    ProductQueryRepository,
)
from shared.domain.requests.product import (
    CreateProductRequest,
    UpdateProductRequest,
)
from shared.errors import (
    err_failed_count_stock,
    err_failed_delete_all_products_permanent,
    err_failed_delete_image_product,
)
from shared.observability import Observability


class ProductCommandServiceImpl:
    def __init__(
        self,
        repo: ProductCommandRepository,
        query_repo: ProductQueryRepository,
        category_repo: CategoryQueryRepository,
        merchant_repo: MerchantQueryRepository,
        cache: ProductCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._query_repo = query_repo
        self._category_repo = category_repo
        self._merchant_repo = merchant_repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(self, request: CreateProductRequest) -> CreateProductRow:
        with self._obs.span(
            "product.command.create",
            merchant_id=request.merchant_id,
            category_id=request.category_id,
        ):
            await self._category_repo.find_by_id(request.category_id)
            await self._merchant_repo.find_by_id(request.merchant_id)
            request.slug_product = generate_slug(request.name)
            row = await self._repo.create(request)
            await self._cache.delete_cached_product(row.product_id)
            return row

    async def update(self, request: UpdateProductRequest) -> UpdateProductRow:
        with self._obs.span(
            "product.command.update",
            product_id=request.product_id,
            merchant_id=request.merchant_id,
            category_id=request.category_id,
        ):
            await self._category_repo.find_by_id(request.category_id)
            await self._merchant_repo.find_by_id(request.merchant_id)
            request.slug_product = generate_slug(request.name)
            row = await self._repo.update(request)
            await self._cache.delete_cached_product(row.product_id)
            return row

    async def update_product_count_stock(self, product_id: int, stock: int) -> UpdateProductCountStockRow:
        with self._obs.span(
            "product.command.update_product_count_stock",
            product_id=product_id,
            stock=stock,
        ):
            if product_id <= 0 or stock < 0:
                raise err_failed_count_stock
            row = await self._repo.update_product_count_stock(product_id, stock)
            await self._cache.delete_cached_product(product_id)
            return row

    async def adjust_product_stock(
        self, product_id: int, delta: int, operation_id: str
    ) -> AdjustProductStockRow:
        with self._obs.span(
            "product.command.adjust_product_stock",
            product_id=product_id,
            delta=delta,
        ):
            if product_id <= 0 or delta == 0 or operation_id == "":
                raise err_failed_count_stock
            row = await self._repo.adjust_product_stock(product_id, delta, operation_id)
            await self._cache.delete_cached_product(product_id)
            return row

    async def trash(self, product_id: int) -> Product:
        with self._obs.span("product.command.trash", product_id=product_id):
            row = await self._repo.trash(product_id)
            await self._cache.delete_cached_product(product_id)
            return row

    async def restore(self, product_id: int) -> Product:
        with self._obs.span("product.command.restore", product_id=product_id):
            row = await self._repo.restore(product_id)
            await self._cache.delete_cached_product(product_id)
            return row

    async def delete_permanent(self, product_id: int) -> bool:
        with self._obs.span("product.command.delete_permanent", product_id=product_id):
            product = await self._query_repo.find_by_id_trashed(product_id)
            image = product.image_product
            if image:
                try:
                    os.remove(image)
                except FileNotFoundError:
                    pass
                except OSError as exc:
                    raise err_failed_delete_image_product.with_internal(exc) from exc
            success = await self._repo.delete_permanent(product_id)
            await self._cache.delete_cached_product(product_id)
            return success

    async def restore_all(self) -> bool:
        with self._obs.span("product.command.restore_all"):
            return await self._repo.restore_all()

    async def delete_all(self) -> bool:
        with self._obs.span("product.command.delete_all"):
            try:
                return await self._repo.delete_all()
            except Exception as exc:
                raise err_failed_delete_all_products_permanent.with_internal(exc) from exc


__all__ = ["ProductCommandServiceImpl"]
