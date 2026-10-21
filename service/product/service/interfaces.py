"""product service"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.product import (
    AdjustProductStockRow,
    CreateProductRow,
    GetProductByIDRow,
    GetProductsActiveRow,
    GetProductsByCategoryNameRow,
    GetProductsByMerchantRow,
    GetProductsRow,
    GetProductsTrashedRow,
    Product,
    UpdateProductCountStockRow,
    UpdateProductRow,
)
from shared.domain.requests.product import (
    CreateProductRequest,
    UpdateProductRequest,
)


class ProductQueryService(Protocol):
    async def find_all(self, search: str, page: int, page_size: int) -> tuple[list[GetProductsRow], int]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetProductsActiveRow], int]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetProductsTrashedRow], int]: ...

    async def find_by_merchant(
        self,
        merchant_id: int,
        category_id: int,
        search: str,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
    ) -> tuple[list[GetProductsByMerchantRow], int]: ...

    async def find_by_category(
        self,
        category_name: str,
        search: str,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
    ) -> tuple[list[GetProductsByCategoryNameRow], int]: ...

    async def find_by_id(self, product_id: int) -> GetProductByIDRow: ...


class ProductCommandService(Protocol):
    async def create(self, request: CreateProductRequest) -> CreateProductRow: ...

    async def update(self, request: UpdateProductRequest) -> UpdateProductRow: ...

    async def update_product_count_stock(self, product_id: int, stock: int) -> UpdateProductCountStockRow: ...

    async def adjust_product_stock(
        self, product_id: int, delta: int, operation_id: str
    ) -> AdjustProductStockRow: ...

    async def trash(self, product_id: int) -> Product: ...

    async def restore(self, product_id: int) -> Product: ...

    async def delete_permanent(self, product_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


__all__ = [
    "ProductCommandService",
    "ProductQueryService",
]
