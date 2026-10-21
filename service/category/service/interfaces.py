"""Category service"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.category import (
    Category,
    CreateCategoryRow,
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
    UpdateCategoryRow,
)
from shared.domain.requests.category import CreateCategoryRequest, UpdateCategoryRequest


class CategoryQueryService(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetCategoriesRow], int]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetCategoriesActiveRow], int]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetCategoriesActiveRow], int]: ...

    async def find_by_id(self, category_id: int) -> GetCategoryByIDRow: ...


class CategoryCommandService(Protocol):
    async def create(self, request: CreateCategoryRequest) -> CreateCategoryRow: ...

    async def update(self, request: UpdateCategoryRequest) -> UpdateCategoryRow: ...

    async def trash(self, category_id: int) -> Category: ...

    async def restore(self, category_id: int) -> Category: ...

    async def delete_permanent(self, category_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


class CategoryStatsService(Protocol):
    async def find_monthly_total_price(
        self, year: int, month: int
    ) -> list[GetMonthlyTotalPriceRow]: ...

    async def find_yearly_total_price(
        self, year: int
    ) -> list[GetYearlyTotalPriceRow]: ...

    async def find_month_price(self, year: int) -> list[GetMonthlyCategoryRow]: ...

    async def find_year_price(self, year: int) -> list[GetYearlyCategoryRow]: ...


class CategoryStatsByIdService(Protocol):
    async def find_monthly_total_price_by_id(
        self, year: int, month: int, category_id: int
    ) -> list[GetMonthlyTotalPriceByIdRow]: ...

    async def find_yearly_total_price_by_id(
        self, year: int, category_id: int
    ) -> list[GetYearlyTotalPriceByIdRow]: ...

    async def find_month_price_by_id(
        self, year: int, category_id: int
    ) -> list[GetMonthlyCategoryByIdRow]: ...

    async def find_year_price_by_id(
        self, year: int, category_id: int
    ) -> list[GetYearlyCategoryByIdRow]: ...


class CategoryStatsByMerchantService(Protocol):
    async def find_monthly_total_price_by_merchant(
        self, year: int, month: int, merchant_id: int
    ) -> list[GetMonthlyTotalPriceByMerchantRow]: ...

    async def find_yearly_total_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetYearlyTotalPriceByMerchantRow]: ...

    async def find_month_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetMonthlyCategoryByMerchantRow]: ...

    async def find_year_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetYearlyCategoryByMerchantRow]: ...


__all__ = [
    "CategoryCommandService",
    "CategoryQueryService",
    "CategoryStatsByIdService",
    "CategoryStatsByMerchantService",
    "CategoryStatsService",
]
