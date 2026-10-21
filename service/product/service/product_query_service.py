"""product query service. Reads are cache-first; a miss loads from the DB and populates the cache with the page and its window `total_count` (taken from the first row; 0 when the page is empty). NORMALISATION: clamps `page <= 0 → 1` / `pageSize <= 0 → 10` inside the service. Like the other domains, that clamp lives in the gRPC handler (`normalize_page`), so the service receives already-normalised paging."""

from __future__ import annotations

from pkg.database.schema.product import (
    GetProductByIDRow,
    GetProductsActiveRow,
    GetProductsByCategoryNameRow,
    GetProductsByMerchantRow,
    GetProductsRow,
    GetProductsTrashedRow,
)
from pkg.logger.logger import Logger
from service.product.redis.interfaces import ProductQueryCache
from service.product.repository.interfaces import ProductQueryRepository
from shared.observability import Observability


class ProductQueryServiceImpl:
    def __init__(
        self,
        repo: ProductQueryRepository,
        cache: ProductQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(self, search: str, page: int, page_size: int) -> tuple[list[GetProductsRow], int]:
        with self._obs.span("product.query.find_all", page=page, page_size=page_size):
            cached = await self._cache.get_products(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_all(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_products(page, page_size, search, rows, total)
            return rows, total

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetProductsActiveRow], int]:
        with self._obs.span("product.query.find_active", page=page, page_size=page_size):
            cached = await self._cache.get_products_active(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_active(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_products_active(page, page_size, search, rows, total)
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetProductsTrashedRow], int]:
        with self._obs.span("product.query.find_trashed", page=page, page_size=page_size):
            cached = await self._cache.get_products_trashed(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_trashed(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_products_trashed(page, page_size, search, rows, total)
            return rows, total

    async def find_by_merchant(
        self,
        merchant_id: int,
        category_id: int,
        search: str,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
    ) -> tuple[list[GetProductsByMerchantRow], int]:
        with self._obs.span(
            "product.query.find_by_merchant",
            merchant_id=merchant_id,
            category_id=category_id,
            page=page,
            page_size=page_size,
        ):
            cached = await self._cache.get_products_by_merchant(
                merchant_id,
                category_id,
                min_price,
                max_price,
                page,
                page_size,
                search,
            )
            if cached is not None:
                return cached
            rows = await self._repo.find_by_merchant(
                merchant_id,
                category_id,
                search,
                min_price,
                max_price,
                page,
                page_size,
            )
            total = rows[0].total_count if rows else 0
            await self._cache.set_products_by_merchant(
                merchant_id,
                category_id,
                min_price,
                max_price,
                page,
                page_size,
                search,
                rows,
                total,
            )
            return rows, total

    async def find_by_category(
        self,
        category_name: str,
        search: str,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
    ) -> tuple[list[GetProductsByCategoryNameRow], int]:
        with self._obs.span(
            "product.query.find_by_category",
            category_name=category_name,
            page=page,
            page_size=page_size,
        ):
            cached = await self._cache.get_products_by_category(
                category_name, min_price, max_price, page, page_size, search
            )
            if cached is not None:
                return cached
            rows = await self._repo.find_by_category(
                category_name, search, min_price, max_price, page, page_size
            )
            total = rows[0].total_count if rows else 0
            await self._cache.set_products_by_category(
                category_name,
                min_price,
                max_price,
                page,
                page_size,
                search,
                rows,
                total,
            )
            return rows, total

    async def find_by_id(self, product_id: int) -> GetProductByIDRow:
        with self._obs.span("product.query.find_by_id", product_id=product_id):
            cached = await self._cache.get_product(product_id)
            if cached is not None:
                return cached
            row = await self._repo.find_by_id(product_id)
            await self._cache.set_product(row)
            return row


__all__ = ["ProductQueryServiceImpl"]
