"""product request DTOs. `price` is also `CHECK (price >= 0)` in the DDL; `required` already rejects 0, so `ge=1` matches both. The gateway fills `image_product` from the uploaded file (see the handler), so a REST create/update needs an image."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateProductRequest(BaseModel):
    merchant_id: int = Field(..., ge=1)
    category_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    price: int = Field(..., ge=1)
    count_in_stock: int = Field(..., ge=1)
    brand: str = Field(..., min_length=1)
    weight: int = Field(..., ge=1)
    rating: int
    slug_product: str = ""
    image_product: str = Field(..., min_length=1)


class UpdateProductRequest(BaseModel):
    product_id: int | None = None
    merchant_id: int = Field(..., ge=1)
    category_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    price: int = Field(..., ge=1)
    count_in_stock: int = Field(..., ge=1)
    brand: str = Field(..., min_length=1)
    weight: int = Field(..., ge=1)
    rating: int
    slug_product: str = ""
    image_product: str = Field(..., min_length=1)


__all__ = [
    "CreateProductRequest",
    "UpdateProductRequest",
]
