"""product cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.product import (
    GetProductByIDRow,
    GetProductsActiveRow,
    GetProductsByCategoryNameRow,
    GetProductsByMerchantRow,
    GetProductsRow,
    GetProductsTrashedRow,
)


class ProductQueryCache(Protocol):
    async def get_products(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetProductsRow], int] | None: ...

    async def set_products(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetProductsRow],
        total: int,
    ) -> None: ...

    async def get_products_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetProductsActiveRow], int] | None: ...

    async def set_products_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetProductsActiveRow],
        total: int,
    ) -> None: ...

    async def get_products_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetProductsTrashedRow], int] | None: ...

    async def set_products_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetProductsTrashedRow],
        total: int,
    ) -> None: ...

    async def get_products_by_merchant(
        self,
        merchant_id: int,
        category_id: int,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
        search: str,
    ) -> tuple[list[GetProductsByMerchantRow], int] | None: ...

    async def set_products_by_merchant(
        self,
        merchant_id: int,
        category_id: int,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetProductsByMerchantRow],
        total: int,
    ) -> None: ...

    async def get_products_by_category(
        self,
        category_name: str,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
        search: str,
    ) -> tuple[list[GetProductsByCategoryNameRow], int] | None: ...

    async def set_products_by_category(
        self,
        category_name: str,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetProductsByCategoryNameRow],
        total: int,
    ) -> None: ...

    async def get_product(self, product_id: int) -> GetProductByIDRow | None: ...

    async def set_product(self, row: GetProductByIDRow) -> None: ...


class ProductCommandCache(Protocol):
    async def delete_cached_product(self, product_id: int) -> int: ...


__all__ = [
    "ProductCommandCache",
    "ProductQueryCache",
]
