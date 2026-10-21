"""Category read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page and the `ORDER BY created_at DESC` ordering (banner has none — do not unify). the `WHERE ($1::TEXT IS NULL OR name ILIKE...)` first branch is dead: the handler always passes a non-null `search` string, so an empty search matches everything through `ILIKE '%%'`. keeps only the effective predicate and documents the omission."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.category import (
    Category,
    GetCategoriesActiveRow,
    GetCategoriesRow,
    GetCategoryByIDRow,
)
from shared.errors import err_category_not_found

_GET_CATEGORIES = """
SELECT
    category_id,
    name,
    description,
    slug_category,
    image_category,
    created_at,
    updated_at,
    COUNT(*) OVER () AS total_count
FROM categories
WHERE
    deleted_at IS NULL
    AND (
        name ILIKE '%' || :search || '%'
        OR slug_category ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_CATEGORIES_ACTIVE = """
SELECT
    category_id,
    name,
    description,
    slug_category,
    image_category,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM categories
WHERE
    deleted_at IS NULL
    AND (
        name ILIKE '%' || :search || '%'
        OR slug_category ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_CATEGORIES_TRASHED = """
SELECT
    category_id,
    name,
    description,
    slug_category,
    image_category,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM categories
WHERE
    deleted_at IS NOT NULL
    AND (
        name ILIKE '%' || :search || '%'
        OR slug_category ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_CATEGORY_BY_ID = """
SELECT
    category_id,
    name,
    description,
    slug_category,
    image_category,
    created_at,
    updated_at
FROM categories
WHERE
    category_id = :category_id
    AND deleted_at IS NULL
"""

_GET_CATEGORY_BY_ID_TRASHED = """
SELECT
    category_id,
    name,
    description,
    slug_category,
    image_category,
    created_at,
    updated_at,
    deleted_at
FROM categories
WHERE
    category_id = :category_id
    AND deleted_at IS NOT NULL
"""


class CategoryQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetCategoriesRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_CATEGORIES,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetCategoriesRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetCategoriesActiveRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_CATEGORIES_ACTIVE,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetCategoriesActiveRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetCategoriesActiveRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_CATEGORIES_TRASHED,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetCategoriesActiveRow.from_row(row) for row in rows]

    async def find_by_id(self, category_id: int) -> GetCategoryByIDRow:
        row = await self._db.scalar(_GET_CATEGORY_BY_ID, {"category_id": category_id})
        if row is None:
            raise err_category_not_found.with_internal(NoRowsError())
        return GetCategoryByIDRow.from_row(row)

    async def find_by_id_trashed(self, category_id: int) -> Category:
        row = await self._db.scalar(
            _GET_CATEGORY_BY_ID_TRASHED, {"category_id": category_id}
        )
        if row is None:
            raise err_category_not_found.with_internal(NoRowsError())
        return Category.from_row(row)


__all__ = ["CategoryQueryRepositoryImpl"]
