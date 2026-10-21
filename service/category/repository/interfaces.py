"""Category repository"""

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


class CategoryQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetCategoriesRow]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetCategoriesActiveRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetCategoriesActiveRow]: ...

    async def find_by_id(self, category_id: int) -> GetCategoryByIDRow: ...

    async def find_by_id_trashed(self, category_id: int) -> Category: ...


class CategoryCommandRepository(Protocol):
    async def create(self, request: CreateCategoryRequest) -> CreateCategoryRow: ...

    async def update(self, request: UpdateCategoryRequest) -> UpdateCategoryRow: ...

    async def trash(self, category_id: int) -> Category: ...

    async def restore(self, category_id: int) -> Category: ...

    async def delete_permanent(self, category_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


class CategoryStatsRepository(Protocol):
    async def get_monthly_total_price(
        self, year: int, month: int
    ) -> list[GetMonthlyTotalPriceRow]: ...

    async def get_yearly_total_prices(
        self, year: int
    ) -> list[GetYearlyTotalPriceRow]: ...

    async def get_month_price(self, year: int) -> list[GetMonthlyCategoryRow]: ...

    async def get_year_price(self, year: int) -> list[GetYearlyCategoryRow]: ...


class CategoryStatsByIdRepository(Protocol):
    async def get_monthly_total_price_by_id(
        self, year: int, month: int, category_id: int
    ) -> list[GetMonthlyTotalPriceByIdRow]: ...

    async def get_yearly_total_prices_by_id(
        self, year: int, category_id: int
    ) -> list[GetYearlyTotalPriceByIdRow]: ...

    async def get_month_price_by_id(
        self, year: int, category_id: int
    ) -> list[GetMonthlyCategoryByIdRow]: ...

    async def get_year_price_by_id(
        self, year: int, category_id: int
    ) -> list[GetYearlyCategoryByIdRow]: ...


class CategoryStatsByMerchantRepository(Protocol):
    async def get_monthly_total_price_by_merchant(
        self, year: int, month: int, merchant_id: int
    ) -> list[GetMonthlyTotalPriceByMerchantRow]: ...

    async def get_yearly_total_prices_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetYearlyTotalPriceByMerchantRow]: ...

    async def get_month_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetMonthlyCategoryByMerchantRow]: ...

    async def get_year_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> list[GetYearlyCategoryByMerchantRow]: ...


__all__ = [
    "CategoryCommandRepository",
    "CategoryQueryRepository",
    "CategoryStatsByIdRepository",
    "CategoryStatsByMerchantRepository",
    "CategoryStatsRepository",
]
