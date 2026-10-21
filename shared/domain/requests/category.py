"""Category request DTOs. Pagination clamps like the handler (page <= 0 -> 1, page_size <= 0 -> 10, page_size capped at 100). The stats DTOs carry the year/month/id triples the three stats services read; they are kept for even though the service layer takes the fields as primitives."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class FindAllCategory(BaseModel):
    search: str = ""
    page: int = 1
    page_size: int = 10

    @model_validator(mode="after")
    def _clamp_pagination(self) -> FindAllCategory:
        if self.page <= 0:
            self.page = 1
        if self.page_size <= 0:
            self.page_size = 10
        if self.page_size > 100:
            self.page_size = 100
        return self


class CreateCategoryRequest(BaseModel):
    """Matches the expected `validator` tags: `name`, `description` and `image_category` are `required` (non-empty). `slug_category` is a `*string` in and the gRPC handler always sets the pointer (even when empty), so it is optional here."""

    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    slug_category: str = ""
    image_category: str = Field(..., min_length=1)


class UpdateCategoryRequest(BaseModel):
    category_id: int | None = None
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    slug_category: str = ""
    image_category: str = Field(..., min_length=1)


# ---- stats request DTOs ----


class MonthTotalPrice(BaseModel):
    year: int = 0
    month: int = 0


class MonthTotalPriceCategory(BaseModel):
    category_id: int = 0
    year: int = 0
    month: int = 0


class YearTotalPriceCategory(BaseModel):
    category_id: int = 0
    year: int = 0


class MonthTotalPriceMerchant(BaseModel):
    merchant_id: int = 0
    year: int = 0
    month: int = 0


class YearTotalPriceMerchant(BaseModel):
    merchant_id: int = 0
    year: int = 0


class MonthPriceMerchant(BaseModel):
    merchant_id: int = 0
    year: int = 0


class YearPriceMerchant(BaseModel):
    merchant_id: int = 0
    year: int = 0


class MonthPriceId(BaseModel):
    category_id: int = 0
    year: int = 0


class YearPriceId(BaseModel):
    category_id: int = 0
    year: int = 0


__all__ = [
    "CreateCategoryRequest",
    "FindAllCategory",
    "MonthPriceId",
    "MonthPriceMerchant",
    "MonthTotalPrice",
    "MonthTotalPriceCategory",
    "MonthTotalPriceMerchant",
    "UpdateCategoryRequest",
    "YearPriceId",
    "YearPriceMerchant",
    "YearTotalPriceCategory",
    "YearTotalPriceMerchant",
]
