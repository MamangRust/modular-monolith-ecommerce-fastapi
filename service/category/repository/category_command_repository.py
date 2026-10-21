"""Category write repository. Soft delete uses `deleted_at`; `delete_permanent` and the bulk operations are hard deletes. A foreign-key violation on the hard deletes maps to a 409 `"cannot permanently delete category while related products exist"`, exactly. Unlike banner, `create`/`update` do **not** translate a unique violation to 409: wraps every error in `ErrCreateCategory`/`ErrUpdateCategory` (500), so behaviour."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.errors import NoRowsError, is_foreign_key_violation
from pkg.database.schema.category import (
    Category,
    CreateCategoryRow,
    UpdateCategoryRow,
)
from shared.domain.requests.category import CreateCategoryRequest, UpdateCategoryRequest
from shared.errors import (
    AppError,
    err_category_not_found,
    err_create_category,
    err_delete_all_permanent_categories,
    err_delete_category_permanently,
    err_restore_all_categories,
    err_restore_category,
    err_trashed_category,
    err_update_category,
    new_conflict_error,
)

_CREATE_CATEGORY = """
INSERT INTO categories (name, description, slug_category, image_category)
VALUES (:name, :description, :slug_category, :image_category)
RETURNING
    category_id,
    name,
    description,
    slug_category,
    image_category,
    created_at,
    updated_at
"""

_UPDATE_CATEGORY = """
UPDATE categories
SET
    name = :name,
    description = :description,
    slug_category = :slug_category,
    image_category = :image_category,
    updated_at = CURRENT_TIMESTAMP
WHERE
    category_id = :category_id
    AND deleted_at IS NULL
RETURNING
    category_id,
    name,
    description,
    slug_category,
    image_category,
    created_at,
    updated_at
"""

_TRASH_CATEGORY = """
UPDATE categories
SET deleted_at = current_timestamp
WHERE
    category_id = :category_id
    AND deleted_at IS NULL
RETURNING
    category_id,
    name,
    description,
    slug_category,
    image_category,
    created_at,
    updated_at,
    deleted_at
"""

_RESTORE_CATEGORY = """
UPDATE categories
SET deleted_at = NULL
WHERE
    category_id = :category_id
    AND deleted_at IS NOT NULL
RETURNING
    category_id,
    name,
    description,
    slug_category,
    image_category,
    created_at,
    updated_at,
    deleted_at
"""

_DELETE_CATEGORY_PERMANENTLY = """
DELETE FROM categories
WHERE
    category_id = :category_id
    AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_CATEGORIES = (
    "UPDATE categories SET deleted_at = NULL WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_PERMANENT_CATEGORIES = "DELETE FROM categories WHERE deleted_at IS NOT NULL"

_RELATED_PRODUCTS_CONFLICT = (
    "cannot permanently delete category while related products exist"
)


class CategoryCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(self, request: CreateCategoryRequest) -> CreateCategoryRow:
        params = {
            "name": request.name,
            "description": request.description,
            "slug_category": request.slug_category,
            "image_category": request.image_category,
        }
        try:
            row = await self._db.execute(_CREATE_CATEGORY, params)
        except Exception as exc:
            raise err_create_category.with_internal(exc) from exc
        if row is None:
            raise err_category_not_found.with_internal(NoRowsError())
        return CreateCategoryRow.from_row(row)

    async def update(self, request: UpdateCategoryRequest) -> UpdateCategoryRow:
        params = {
            "category_id": request.category_id,
            "name": request.name,
            "description": request.description,
            "slug_category": request.slug_category,
            "image_category": request.image_category,
        }
        try:
            row = await self._db.execute(_UPDATE_CATEGORY, params)
        except Exception as exc:
            raise err_update_category.with_internal(exc) from exc
        if row is None:
            raise err_category_not_found.with_internal(NoRowsError())
        return UpdateCategoryRow.from_row(row)

    async def trash(self, category_id: int) -> Category:
        try:
            row = await self._db.execute(_TRASH_CATEGORY, {"category_id": category_id})
        except Exception as exc:
            raise err_trashed_category.with_internal(exc) from exc
        if row is None:
            raise err_category_not_found.with_internal(NoRowsError())
        return Category.from_row(row)

    async def restore(self, category_id: int) -> Category:
        try:
            row = await self._db.execute(
                _RESTORE_CATEGORY, {"category_id": category_id}
            )
        except Exception as exc:
            raise err_restore_category.with_internal(exc) from exc
        if row is None:
            raise err_category_not_found.with_internal(NoRowsError())
        return Category.from_row(row)

    async def delete_permanent(self, category_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_CATEGORY_PERMANENTLY, {"category_id": category_id}
            )
        except AppError:
            raise
        except Exception as exc:
            if is_foreign_key_violation(exc):
                raise new_conflict_error(_RELATED_PRODUCTS_CONFLICT).with_internal(
                    exc
                ) from exc
            raise err_delete_category_permanently.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_CATEGORIES)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_categories.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_CATEGORIES)
        except AppError:
            raise
        except Exception as exc:
            if is_foreign_key_violation(exc):
                raise new_conflict_error(_RELATED_PRODUCTS_CONFLICT).with_internal(
                    exc
                ) from exc
            raise err_delete_all_permanent_categories.with_internal(exc) from exc
        return True


__all__ = ["CategoryCommandRepositoryImpl"]
