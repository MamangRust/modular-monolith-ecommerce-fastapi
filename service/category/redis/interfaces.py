"""Category cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.category import (
    GetCategoriesActiveRow,
    GetCategoriesRow,
    GetCategoryByIDRow,
    GetMonthlyCategoryByIdRow,
    GetMonthlyCategoryByMerchantRow,
    GetMonthlyCategoryRow,
    GetMonthlyTotalPriceByIdRow,
    GetMonthlyTotalPriceByMerchantRow,
    GetMonthlyTotalPriceRow,
    GetYearlyCategoryByIdRow,
    GetYearlyCategoryByMerchantRow,
    GetYearlyCategoryRow,
    GetYearlyTotalPriceByIdRow,
    GetYearlyTotalPriceByMerchantRow,
    GetYearlyTotalPriceRow,
)


class CategoryQueryCache(Protocol):
    async def get_categories(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetCategoriesRow], int] | None: ...

    async def set_categories(
        self,
        page: int,
        page_size: int,
        search: str,
        categories: list[GetCategoriesRow],
        total: int,
    ) -> None: ...

    async def get_category_by_id(
        self, category_id: int
    ) -> GetCategoryByIDRow | None: ...

    async def set_category_by_id(self, category: GetCategoryByIDRow) -> None: ...

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetCategoriesActiveRow], int] | None: ...

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        categories: list[GetCategoriesActiveRow],
        total: int,
    ) -> None: ...

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetCategoriesActiveRow], int] | None: ...

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        categories: list[GetCategoriesActiveRow],
        total: int,
    ) -> None: ...


class CategoryCommandCache(Protocol):
    async def delete_cached_category(self, category_id: int) -> int: ...

    async def invalidate_lists(self) -> int: ...

    async def invalidate_category(self, category_id: int) -> int: ...

    async def invalidate_all(self) -> int: ...


class CategoryStatsCache(Protocol):
    async def get_month_total_price(
        self, year: int, month: int
    ) -> list[GetMonthlyTotalPriceRow] | None: ...

    async def set_month_total_price(
        self, year: int, month: int, rows: list[GetMonthlyTotalPriceRow]
    ) -> None: ...

    async def get_year_total_price(
        self, year: int
    ) -> list[GetYearlyTotalPriceRow] | None: ...

    async def set_year_total_price(
        self, year: int, rows: list[GetYearlyTotalPriceRow]
    ) -> None: ...

    async def get_month_price(
        self, year: int
    ) -> list[GetMonthlyCategoryRow] | None: ...

    async def set_month_price(
        self, year: int, rows: list[GetMonthlyCategoryRow]
    ) -> None: ...

    async def get_year_price(self, year: int) -> list[GetYearlyCategoryRow] | None: ...

    async def set_year_price(
        self, year: int, rows: list[GetYearlyCategoryRow]
    ) -> None: ...


class CategoryStatsByIdCache(Protocol):
    async def get_month_total_price_by_id(
        self, category_id: int, year: int, month: int
    ) -> list[GetMonthlyTotalPriceByIdRow] | None: ...

    async def set_month_total_price_by_id(
        self,
        category_id: int,
        year: int,
        month: int,
        rows: list[GetMonthlyTotalPriceByIdRow],
    ) -> None: ...

    async def get_year_total_price_by_id(
        self, category_id: int, year: int
    ) -> list[GetYearlyTotalPriceByIdRow] | None: ...

    async def set_year_total_price_by_id(
        self, category_id: int, year: int, rows: list[GetYearlyTotalPriceByIdRow]
    ) -> None: ...

    async def get_month_price_by_id(
        self, category_id: int, year: int
    ) -> list[GetMonthlyCategoryByIdRow] | None: ...

    async def set_month_price_by_id(
        self, category_id: int, year: int, rows: list[GetMonthlyCategoryByIdRow]
    ) -> None: ...

    async def get_year_price_by_id(
        self, category_id: int, year: int
    ) -> list[GetYearlyCategoryByIdRow] | None: ...

    async def set_year_price_by_id(
        self, category_id: int, year: int, rows: list[GetYearlyCategoryByIdRow]
    ) -> None: ...


class CategoryStatsByMerchantCache(Protocol):
    async def get_month_total_price_by_merchant(
        self, merchant_id: int, year: int, month: int
    ) -> list[GetMonthlyTotalPriceByMerchantRow] | None: ...

    async def set_month_total_price_by_merchant(
        self,
        merchant_id: int,
        year: int,
        month: int,
        rows: list[GetMonthlyTotalPriceByMerchantRow],
    ) -> None: ...

    async def get_year_total_price_by_merchant(
        self, merchant_id: int, year: int
    ) -> list[GetYearlyTotalPriceByMerchantRow] | None: ...

    async def set_year_total_price_by_merchant(
        self, merchant_id: int, year: int, rows: list[GetYearlyTotalPriceByMerchantRow]
    ) -> None: ...

    async def get_month_price_by_merchant(
        self, merchant_id: int, year: int
    ) -> list[GetMonthlyCategoryByMerchantRow] | None: ...

    async def set_month_price_by_merchant(
        self, merchant_id: int, year: int, rows: list[GetMonthlyCategoryByMerchantRow]
    ) -> None: ...

    async def get_year_price_by_merchant(
        self, merchant_id: int, year: int
    ) -> list[GetYearlyCategoryByMerchantRow] | None: ...

    async def set_year_price_by_merchant(
        self, merchant_id: int, year: int, rows: list[GetYearlyCategoryByMerchantRow]
    ) -> None: ...


__all__ = [
    "CategoryCommandCache",
    "CategoryQueryCache",
    "CategoryStatsByIdCache",
    "CategoryStatsByMerchantCache",
    "CategoryStatsCache",
]
