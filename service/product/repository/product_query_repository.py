"""product read repository. SQL is kept verbatim from the reference where practical, including the `COUNT(*) OVER` window (FindAll/Active/Trashed) and the `filtered_products` CTE with a scalar `COUNT(*)` subquery (ByMerchant/ByCategory) that supplies `total_count` in the same round trip as the page. Named-parameter adaptations (documented): - the `$1::TEXT IS NULL OR...` search guards are dropped: binds a plain `string` (never nil) and an empty search already matches every row via `ILIKE '%%'`; - `GetProductsByCategoryName`'s price filter is normalised to match `GetProductsByMerchant`: binds `int32(IntPtrToInt(max_price)` (0 when the caller omits it) and tests `price <= 0`, so the category endpoint returns only price-0 products unless a max is supplied. treats 0 as "ignore" (`COALESCE(NULLIF(:max_price, 0), 999999999)`), matching the merchant query. `find_by_id`/`find_by_id_trashed` map a missing row to `err_product_not_found` (404) and any other failure to `err_product_internal` (500)."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.product import (
    GetProductByIDRow,
    GetProductsActiveRow,
    GetProductsByCategoryNameRow,
    GetProductsByMerchantRow,
    GetProductsRow,
    GetProductsTrashedRow,
    Product,
)
from shared.errors import (
    err_find_active_products,
    err_find_all_products,
    err_find_products_by_category,
    err_find_products_by_merchant,
    err_find_trashed_products,
    err_product_internal,
    err_product_not_found,
)

_BASE_COLUMNS = """
    product_id,
    merchant_id,
    category_id,
    name,
    description,
    price,
    count_in_stock,
    brand,
    weight,
    rating,
    slug_product,
    image_product,
    created_at,
    updated_at
"""

_GET_PRODUCTS = f"""
SELECT
{_BASE_COLUMNS},
    COUNT(*) OVER () AS total_count
FROM products as p
WHERE
    deleted_at IS NULL
    AND (
        p.name ILIKE '%' || :search || '%'
        OR p.description ILIKE '%' || :search || '%'
        OR p.brand ILIKE '%' || :search || '%'
        OR p.slug_product ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_PRODUCTS_ACTIVE = f"""
SELECT
{_BASE_COLUMNS},
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM products as p
WHERE
    deleted_at IS NULL
    AND (
        p.name ILIKE '%' || :search || '%'
        OR p.description ILIKE '%' || :search || '%'
        OR p.brand ILIKE '%' || :search || '%'
        OR p.slug_product ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_PRODUCTS_TRASHED = f"""
SELECT
{_BASE_COLUMNS},
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM products as p
WHERE
    deleted_at IS NOT NULL
    AND (
        p.name ILIKE '%' || :search || '%'
        OR p.description ILIKE '%' || :search || '%'
        OR p.brand ILIKE '%' || :search || '%'
        OR p.slug_product ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_PRODUCTS_BY_MERCHANT = """
WITH filtered_products AS (
    SELECT
        p.product_id,
        p.merchant_id,
        p.category_id,
        p.weight,
        p.rating,
        p.slug_product,
        p.name,
        p.description,
        p.price,
        p.count_in_stock,
        p.brand,
        p.image_product,
        p.created_at,
        p.updated_at,
        c.name AS category_name
    FROM products p
        JOIN categories c ON p.category_id = c.category_id
    WHERE
        p.deleted_at IS NULL
        AND p.merchant_id = :merchant_id
        AND (
            p.name ILIKE '%' || COALESCE(:search, '') || '%'
            OR p.description ILIKE '%' || COALESCE(:search, '') || '%'
        )
        AND (
            c.category_id = NULLIF(:category_id, 0)
            OR NULLIF(:category_id, 0) IS NULL
        )
        AND (
            p.price >= COALESCE(NULLIF(:min_price, 0), 0)
            AND p.price <= COALESCE(NULLIF(:max_price, 0), 999999999)
        )
)
SELECT (
        SELECT COUNT(*)
        FROM filtered_products
    ) AS total_count, fp.*
FROM filtered_products fp
ORDER BY fp.created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_PRODUCTS_BY_CATEGORY_NAME = """
WITH filtered_products AS (
    SELECT
        p.product_id,
        p.merchant_id,
        p.category_id,
        p.weight,
        p.rating,
        p.slug_product,
        p.name,
        p.description,
        p.price,
        p.count_in_stock,
        p.brand,
        p.image_product,
        p.created_at,
        p.updated_at,
        c.name AS category_name
    FROM products p
        JOIN categories c ON p.category_id = c.category_id
    WHERE
        p.deleted_at IS NULL
        AND c.name = :category_name
        AND (
            p.name ILIKE '%' || :search || '%'
            OR p.description ILIKE '%' || :search || '%'
        )
        AND (
            p.price >= COALESCE(NULLIF(:min_price, 0), 0)
            AND p.price <= COALESCE(NULLIF(:max_price, 0), 999999999)
        )
)
SELECT (
        SELECT COUNT(*)
        FROM filtered_products
    ) AS total_count, fp.*
FROM filtered_products fp
ORDER BY fp.created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_PRODUCT_BY_ID = f"""
SELECT
{_BASE_COLUMNS}
FROM products
WHERE
    product_id = :product_id
    AND deleted_at IS NULL
"""

_GET_PRODUCT_BY_ID_TRASHED = """
SELECT * FROM products WHERE product_id = :product_id
"""


class ProductQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetProductsRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_PRODUCTS,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_all_products.with_internal(exc) from exc
        return [GetProductsRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetProductsActiveRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_PRODUCTS_ACTIVE,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_active_products.with_internal(exc) from exc
        return [GetProductsActiveRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetProductsTrashedRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_PRODUCTS_TRASHED,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_trashed_products.with_internal(exc) from exc
        return [GetProductsTrashedRow.from_row(row) for row in rows]

    async def find_by_merchant(
        self,
        merchant_id: int,
        category_id: int,
        search: str,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
    ) -> list[GetProductsByMerchantRow]:
        offset = (page - 1) * page_size
        params = {
            "merchant_id": merchant_id,
            "category_id": category_id,
            "search": search,
            "min_price": min_price,
            "max_price": max_price,
            "limit": page_size,
            "offset": offset,
        }
        try:
            rows = await self._db.select(_GET_PRODUCTS_BY_MERCHANT, params)
        except Exception as exc:
            raise err_find_products_by_merchant.with_internal(exc) from exc
        return [GetProductsByMerchantRow.from_row(row) for row in rows]

    async def find_by_category(
        self,
        category_name: str,
        search: str,
        min_price: int,
        max_price: int,
        page: int,
        page_size: int,
    ) -> list[GetProductsByCategoryNameRow]:
        offset = (page - 1) * page_size
        params = {
            "category_name": category_name,
            "search": search,
            "min_price": min_price,
            "max_price": max_price,
            "limit": page_size,
            "offset": offset,
        }
        try:
            rows = await self._db.select(_GET_PRODUCTS_BY_CATEGORY_NAME, params)
        except Exception as exc:
            raise err_find_products_by_category.with_internal(exc) from exc
        return [GetProductsByCategoryNameRow.from_row(row) for row in rows]

    async def find_by_id(self, product_id: int) -> GetProductByIDRow:
        try:
            row = await self._db.scalar(
                _GET_PRODUCT_BY_ID, {"product_id": product_id}
            )
        except Exception as exc:
            raise err_product_internal.with_internal(exc) from exc
        if row is None:
            raise err_product_not_found
        return GetProductByIDRow.from_row(row)

    async def find_by_id_trashed(self, product_id: int) -> Product:
        try:
            row = await self._db.scalar(
                _GET_PRODUCT_BY_ID_TRASHED, {"product_id": product_id}
            )
        except Exception as exc:
            raise err_product_internal.with_internal(exc) from exc
        if row is None:
            raise err_product_not_found
        return Product.from_row(row)


__all__ = ["ProductQueryRepositoryImpl"]
