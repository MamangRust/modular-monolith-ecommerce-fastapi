"""Row types for the categories table. `description`, `slug_category` and `image_category` are nullable at the SQL level (models them as `*string`), so they surface as `str | None`. Timestamps are plain `datetime`; the category handlers format them as `%Y-%m-%d` (unlike banner's millisecond layout). The stats rows are shared by the three stats repositories (base / by-id / by-merchant); the by-id and by-merchant projections are column-identical, so they alias the base dataclasses exactly as reuses the same struct shape."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Category:

    category_id: int
    name: str
    description: str | None
    slug_category: str | None
    image_category: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> Category:
        return cls(
            category_id=row["category_id"],
            name=row["name"],
            description=row.get("description"),
            slug_category=row.get("slug_category"),
            image_category=row.get("image_category"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateCategoryRow:
    category_id: int
    name: str
    description: str | None
    slug_category: str | None
    image_category: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateCategoryRow:
        return cls(
            category_id=row["category_id"],
            name=row["name"],
            description=row.get("description"),
            slug_category=row.get("slug_category"),
            image_category=row.get("image_category"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class GetCategoryByIDRow:
    """`FindByID` projection — active rows only, no `deleted_at`."""

    category_id: int
    name: str
    description: str | None
    slug_category: str | None
    image_category: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetCategoryByIDRow:
        return cls(
            category_id=row["category_id"],
            name=row["name"],
            description=row.get("description"),
            slug_category=row.get("slug_category"),
            image_category=row.get("image_category"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateCategoryRow = GetCategoryByIDRow


@dataclass
class GetCategoriesRow:
    """`FindAll` projection with a window total count."""

    category_id: int
    name: str
    description: str | None
    slug_category: str | None
    image_category: str | None
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetCategoriesRow:
        return cls(
            category_id=row["category_id"],
            name=row["name"],
            description=row.get("description"),
            slug_category=row.get("slug_category"),
            image_category=row.get("image_category"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetCategoriesActiveRow:
    category_id: int
    name: str
    description: str | None
    slug_category: str | None
    image_category: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetCategoriesActiveRow:
        return cls(
            category_id=row["category_id"],
            name=row["name"],
            description=row.get("description"),
            slug_category=row.get("slug_category"),
            image_category=row.get("image_category"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetCategoriesTrashedRow = GetCategoriesActiveRow


# ---- stats rows ----
# The by-id / by-merchant projections share these column sets verbatim, so
# the aliases below mirror reusing one struct shape across the three
# stats repositories.


@dataclass
class GetMonthlyTotalPriceRow:
    year: str
    month: str
    total_revenue: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMonthlyTotalPriceRow:
        return cls(
            year=str(row["year"]),
            month=str(row["month"]),
            total_revenue=int(row["total_revenue"]),
        )


@dataclass
class GetYearlyTotalPriceRow:
    year: str
    total_revenue: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetYearlyTotalPriceRow:
        return cls(year=str(row["year"]), total_revenue=int(row["total_revenue"]))


@dataclass
class GetMonthlyCategoryRow:
    month: str
    category_id: int
    category_name: str
    order_count: int
    items_sold: int
    total_revenue: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMonthlyCategoryRow:
        return cls(
            month=str(row["month"]),
            category_id=int(row["category_id"]),
            category_name=str(row["category_name"]),
            order_count=int(row["order_count"]),
            items_sold=int(row["items_sold"]),
            total_revenue=int(row["total_revenue"]),
        )


@dataclass
class GetYearlyCategoryRow:
    year: str
    category_id: int
    category_name: str
    order_count: int
    items_sold: int
    total_revenue: int
    unique_products_sold: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetYearlyCategoryRow:
        return cls(
            year=str(row["year"]),
            category_id=int(row["category_id"]),
            category_name=str(row["category_name"]),
            order_count=int(row["order_count"]),
            items_sold=int(row["items_sold"]),
            total_revenue=int(row["total_revenue"]),
            unique_products_sold=int(row["unique_products_sold"]),
        )


GetMonthlyTotalPriceByIdRow = GetMonthlyTotalPriceRow
GetYearlyTotalPriceByIdRow = GetYearlyTotalPriceRow
GetMonthlyTotalPriceByMerchantRow = GetMonthlyTotalPriceRow
GetYearlyTotalPriceByMerchantRow = GetYearlyTotalPriceRow
GetMonthlyCategoryByIdRow = GetMonthlyCategoryRow
GetMonthlyCategoryByMerchantRow = GetMonthlyCategoryRow
GetYearlyCategoryByIdRow = GetYearlyCategoryRow
GetYearlyCategoryByMerchantRow = GetYearlyCategoryRow


__all__ = [
    "Category",
    "CreateCategoryRow",
    "GetCategoriesActiveRow",
    "GetCategoriesRow",
    "GetCategoriesTrashedRow",
    "GetCategoryByIDRow",
    "GetMonthlyCategoryByMerchantRow",
    "GetMonthlyCategoryByIdRow",
    "GetMonthlyCategoryRow",
    "GetMonthlyTotalPriceByMerchantRow",
    "GetMonthlyTotalPriceByIdRow",
    "GetMonthlyTotalPriceRow",
    "GetYearlyCategoryByMerchantRow",
    "GetYearlyCategoryByIdRow",
    "GetYearlyCategoryRow",
    "GetYearlyTotalPriceByMerchantRow",
    "GetYearlyTotalPriceByIdRow",
    "GetYearlyTotalPriceRow",
    "UpdateCategoryRow",
]
