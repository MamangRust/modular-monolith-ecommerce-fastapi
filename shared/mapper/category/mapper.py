"""Category row/proto -> response DTO mapping. Two input shapes, one output: - row dataclasses — format the timestamps the way the handlers do (`%Y-%m-%d`); - proto messages — already-formatted strings, passed through unchanged. The seeder and gateway always populate them, so the two agree in practice (see Planning.md)."""

from __future__ import annotations

from typing import Any

from pkg.database.schema.category import (
    Category,
    CreateCategoryRow,
    GetCategoriesActiveRow,
    GetCategoriesRow,
    GetCategoryByIDRow,
    UpdateCategoryRow,
)
from shared.convert.convert import format_date
from shared.domain.response.category import (
    CategoryResponse,
    CategoryResponseDeleteAt,
)

CategoryRow = (
    Category
    | CreateCategoryRow
    | GetCategoryByIDRow
    | GetCategoriesRow
    | UpdateCategoryRow
)
CategoryDeleteAtRow = Category | GetCategoriesActiveRow


def to_category_response(row: CategoryRow) -> CategoryResponse:
    return CategoryResponse(
        id=row.category_id,
        name=row.name,
        description=row.description or "",
        slug_category=row.slug_category or "",
        image_category=row.image_category or "",
        created_at=format_date(row.created_at),
        updated_at=format_date(row.updated_at),
    )


def to_category_response_delete_at(
    row: CategoryDeleteAtRow,
) -> CategoryResponseDeleteAt:
    return CategoryResponseDeleteAt(
        id=row.category_id,
        name=row.name,
        description=row.description or "",
        slug_category=row.slug_category or "",
        image_category=row.image_category or "",
        created_at=format_date(row.created_at),
        updated_at=format_date(row.updated_at),
        deleted_at=format_date(row.deleted_at) or None,
    )


def map_category_response(pb: Any) -> CategoryResponse:
    return CategoryResponse(
        id=int(pb.id),
        name=pb.name,
        description=pb.description,
        slug_category=pb.slug_category,
        image_category=pb.image_category,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_category_response_delete_at(pb: Any) -> CategoryResponseDeleteAt:
    # always sets the pointer, so an absent wrapper renders as "".
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return CategoryResponseDeleteAt(
        id=int(pb.id),
        name=pb.name,
        description=pb.description,
        slug_category=pb.slug_category,
        image_category=pb.image_category,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


__all__ = [
    "map_category_response",
    "map_category_response_delete_at",
    "to_category_response",
    "to_category_response_delete_at",
]
