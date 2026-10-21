"""product query cache.

Every list cache written here is also read. Reads/writes never raise:
`CacheStore` swallows Redis errors so a cache outage degrades to a DB read."""

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
from service.product.redis.cache import (
    decode_page,
    encode_page,
    product_active_row_from_dict,
    product_active_row_to_dict,
    product_by_id_from_dict,
    product_by_id_to_dict,
    product_merchant_row_from_dict,
    product_merchant_row_to_dict,
    product_row_from_dict,
    product_row_to_dict,
)
from service.product.redis.common import (
    TTL_DEFAULT,
    product_active_key,
    product_all_key,
    product_by_id_key,
    product_category_key,
    product_merchant_key,
    product_trashed_key,
)
from shared.cache import CacheStore


class ProductQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_products(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetProductsRow], int] | None:
        payload = await self._store.get_json(product_all_key(page, page_size, search))
        return decode_page(payload, product_row_from_dict)

    async def set_products(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetProductsRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            product_all_key(page, page_size, search),
            encode_page(rows, total, product_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_products_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetProductsActiveRow], int] | None:
        payload = await self._store.get_json(
            product_active_key(page, page_size, search)
        )
        return decode_page(payload, product_active_row_from_dict)

    async def set_products_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetProductsActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            product_active_key(page, page_size, search),
            encode_page(rows, total, product_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_products_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetProductsTrashedRow], int] | None:
        payload = await self._store.get_json(
            product_trashed_key(page, page_size, search)
        )
        return decode_page(payload, product_active_row_from_dict)

    async def set_products_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetProductsTrashedRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            product_trashed_key(page, page_size, search),
            encode_page(rows, total, product_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_products_by_merchant(
        self,
        merchant_id: int,
        category_id: int,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
        search: str,
    ) -> tuple[list[GetProductsByMerchantRow], int] | None:
        payload = await self._store.get_json(
            product_merchant_key(
                merchant_id,
                category_id,
                min_price,
                max_price,
                page,
                page_size,
                search,
            )
        )
        return decode_page(payload, product_merchant_row_from_dict)

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
    ) -> None:
        await self._store.set_json(
            product_merchant_key(
                merchant_id,
                category_id,
                min_price,
                max_price,
                page,
                page_size,
                search,
            ),
            encode_page(rows, total, product_merchant_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_products_by_category(
        self,
        category_name: str,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
        search: str,
    ) -> tuple[list[GetProductsByCategoryNameRow], int] | None:
        payload = await self._store.get_json(
            product_category_key(
                category_name, min_price, max_price, page, page_size, search
            )
        )
        return decode_page(payload, product_merchant_row_from_dict)

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
    ) -> None:
        await self._store.set_json(
            product_category_key(
                category_name, min_price, max_price, page, page_size, search
            ),
            encode_page(rows, total, product_merchant_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_product(self, product_id: int) -> GetProductByIDRow | None:
        payload = await self._store.get_json(product_by_id_key(product_id))
        if not isinstance(payload, dict):
            return None
        return product_by_id_from_dict(payload)

    async def set_product(self, row: GetProductByIDRow) -> None:
        await self._store.set_json(
            product_by_id_key(row.product_id),
            product_by_id_to_dict(row),
            TTL_DEFAULT,
        )


__all__ = ["ProductQueryCacheImpl"]
