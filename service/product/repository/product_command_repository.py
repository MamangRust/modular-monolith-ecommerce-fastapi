"""product write repository. `create`/`update`/`trash`/`restore` map a missing row (`None` from the `RETURNING` projection) to `err_product_not_found`; every other failure maps to the matching sentinel. NORMALISATION: never binds `CreateProductParams.Rating`/`UpdateProductParams.Rating`, so `create` falls to the DB default `0.0` and `update` sets `rating = NULL`. persists the request `rating` like every other field. `adjust_product_stock` is a data-modifying CTE, so it runs through `Database.execute` (committed) rather than `select` (rolled back)."""

from __future__ import annotations

from typing import Any

from pkg.database.database import Database
from pkg.database.errors import is_foreign_key_violation
from pkg.database.schema.product import (
    AdjustProductStockRow,
    CreateProductRow,
    Product,
    UpdateProductCountStockRow,
    UpdateProductRow,
)
from shared.domain.requests.product import (
    CreateProductRequest,
    UpdateProductRequest,
)
from shared.errors import (
    AppError,
    err_create_product,
    err_delete_all_products,
    err_delete_product_permanent,
    err_product_not_found,
    err_restore_all_products,
    err_restore_product,
    err_trashed_product,
    err_update_product,
    err_update_product_count_stock,
    new_conflict_error,
)

_RETURNING_COLUMNS = """
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

_CREATE_PRODUCT = f"""
INSERT INTO products (
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
    image_product
)
VALUES (
    :merchant_id,
    :category_id,
    :name,
    :description,
    :price,
    :count_in_stock,
    :brand,
    :weight,
    :rating,
    :slug_product,
    :image_product
)
RETURNING
{_RETURNING_COLUMNS}
"""

_UPDATE_PRODUCT = f"""
UPDATE products
SET
    category_id = :category_id,
    name = :name,
    description = :description,
    price = :price,
    count_in_stock = :count_in_stock,
    brand = :brand,
    weight = :weight,
    rating = :rating,
    slug_product = :slug_product,
    image_product = :image_product,
    updated_at = CURRENT_TIMESTAMP
WHERE
    product_id = :product_id
    AND deleted_at IS NULL
RETURNING
{_RETURNING_COLUMNS}
"""

_UPDATE_PRODUCT_COUNT_STOCK = """
UPDATE products
SET
    count_in_stock = :count_in_stock
WHERE
    product_id = :product_id
    AND deleted_at IS NULL
    AND :count_in_stock >= 0
RETURNING
    product_id,
    count_in_stock
"""

_ADJUST_PRODUCT_STOCK = """
WITH existing_adjustment AS (
    SELECT product_id, delta
    FROM product_stock_adjustments psa
    WHERE psa.operation_id = :operation_id
      AND psa.product_id = :product_id
      AND psa.delta = :delta
), new_adjustment AS (
    INSERT INTO product_stock_adjustments (operation_id, product_id, delta)
    SELECT :operation_id, :product_id, :delta
    WHERE NOT EXISTS (SELECT 1 FROM existing_adjustment)
      AND EXISTS (
          SELECT 1
          FROM products
          WHERE product_id = :product_id
            AND deleted_at IS NULL
            AND count_in_stock + :delta >= 0
      )
    ON CONFLICT (operation_id) DO NOTHING
    RETURNING product_id, delta
), applied AS (
    UPDATE products p
    SET count_in_stock = p.count_in_stock + a.delta,
        updated_at = CURRENT_TIMESTAMP
    FROM new_adjustment a
    WHERE p.product_id = a.product_id
      AND p.deleted_at IS NULL
    RETURNING p.product_id, p.count_in_stock
)
SELECT a.product_id, a.count_in_stock
FROM applied a
UNION ALL
SELECT p.product_id, p.count_in_stock
FROM products p
JOIN existing_adjustment e ON e.product_id = p.product_id
WHERE p.deleted_at IS NULL
"""

_TRASH_PRODUCT = f"""
UPDATE products
SET
    deleted_at = current_timestamp
WHERE
    product_id = :product_id
    AND deleted_at IS NULL
RETURNING
{_RETURNING_COLUMNS}
"""

_RESTORE_PRODUCT = f"""
UPDATE products
SET
    deleted_at = NULL
WHERE
    product_id = :product_id
    AND deleted_at IS NOT NULL
RETURNING
{_RETURNING_COLUMNS}
"""

_DELETE_PRODUCT_PERMANENTLY = """
DELETE FROM products
WHERE
    product_id = :product_id
    AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_PRODUCTS = (
    "UPDATE products SET deleted_at = NULL WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_PERMANENT_PRODUCTS = (
    "DELETE FROM products WHERE deleted_at IS NOT NULL"
)


class ProductCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def _returning(
        self, sql: str, params: dict[str, Any]
    ) -> dict[str, Any] | None:
        return await self._db.execute(sql, params)

    async def create(self, request: CreateProductRequest) -> CreateProductRow:
        params = {
            "merchant_id": request.merchant_id,
            "category_id": request.category_id,
            "name": request.name,
            "description": request.description,
            "price": request.price,
            "count_in_stock": request.count_in_stock,
            "brand": request.brand,
            "weight": request.weight,
            "rating": request.rating,
            "slug_product": request.slug_product,
            "image_product": request.image_product,
        }
        try:
            row = await self._returning(_CREATE_PRODUCT, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_create_product.with_internal(exc) from exc
        if row is None:
            raise err_product_not_found
        return CreateProductRow.from_row(row)

    async def update(self, request: UpdateProductRequest) -> UpdateProductRow:
        params = {
            "product_id": request.product_id,
            "category_id": request.category_id,
            "name": request.name,
            "description": request.description,
            "price": request.price,
            "count_in_stock": request.count_in_stock,
            "brand": request.brand,
            "weight": request.weight,
            "rating": request.rating,
            "slug_product": request.slug_product,
            "image_product": request.image_product,
        }
        try:
            row = await self._returning(_UPDATE_PRODUCT, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_update_product.with_internal(exc) from exc
        if row is None:
            raise err_product_not_found
        return UpdateProductRow.from_row(row)

    async def update_product_count_stock(
        self, product_id: int, stock: int
    ) -> UpdateProductCountStockRow:
        try:
            row = await self._returning(
                _UPDATE_PRODUCT_COUNT_STOCK,
                {"product_id": product_id, "count_in_stock": stock},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_update_product_count_stock.with_internal(exc) from exc
        if row is None:
            raise err_product_not_found
        return UpdateProductCountStockRow.from_row(row)

    async def adjust_product_stock(
        self, product_id: int, delta: int, operation_id: str
    ) -> AdjustProductStockRow:
        try:
            row = await self._returning(
                _ADJUST_PRODUCT_STOCK,
                {
                    "operation_id": operation_id,
                    "product_id": product_id,
                    "delta": delta,
                },
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_update_product_count_stock.with_internal(exc) from exc
        if row is None:
            raise err_product_not_found
        return AdjustProductStockRow.from_row(row)

    async def trash(self, product_id: int) -> Product:
        try:
            row = await self._returning(
                _TRASH_PRODUCT, {"product_id": product_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_trashed_product.with_internal(exc) from exc
        if row is None:
            raise err_product_not_found
        return Product.from_row(row)

    async def restore(self, product_id: int) -> Product:
        try:
            row = await self._returning(
                _RESTORE_PRODUCT, {"product_id": product_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_product.with_internal(exc) from exc
        if row is None:
            raise err_product_not_found
        return Product.from_row(row)

    async def delete_permanent(self, product_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_PRODUCT_PERMANENTLY, {"product_id": product_id}
            )
        except AppError:
            raise
        except Exception as exc:
            if is_foreign_key_violation(exc):
                raise new_conflict_error(
                    "cannot permanently delete product while related records exist"
                ).with_internal(exc) from exc
            raise err_delete_product_permanent.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_PRODUCTS)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_products.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_PRODUCTS)
        except AppError:
            raise
        except Exception as exc:
            if is_foreign_key_violation(exc):
                raise new_conflict_error(
                    "cannot permanently delete products while related records exist"
                ).with_internal(exc) from exc
            raise err_delete_all_products.with_internal(exc) from exc
        return True


__all__ = ["ProductCommandRepositoryImpl"]
