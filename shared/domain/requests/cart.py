"""Cart request DTOs. Validation Matches the expected `validator` tags: - create: `quantity` `required,gt=0` -> `ge=1`, `product_id` `required` -> `ge=1`; `user_id` is `omitempty` (unvalidated — the caller supplies it); - delete: `cart_id`/`user_id` `required` -> `ge=1`; - delete-all: `user_id` `required` -> `ge=1`, `cart_ids` `required` (non-empty). `FindAllCarts`/`CartCreateRecord` are internal records (structs), not user input, so they stay plain dataclasses; only the three command DTOs are pydantic-validated (and only in the gRPC handler, matching)."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field


@dataclass
class FindAllCarts:
    """Service/cache request (`requests.FindAllCarts`)."""

    user_id: int
    page: int
    page_size: int
    search: str


@dataclass
class CartCreateRecord:
    """Repository create params (`requests.CartCreateRecord`)."""

    product_id: int
    user_id: int
    name: str
    price: int
    image_product: str
    quantity: int
    weight: int


class CreateCartRequest(BaseModel):
    quantity: int = Field(..., ge=1)
    product_id: int = Field(..., ge=1)
    user_id: int = 0


class DeleteCartRequest(BaseModel):
    cart_id: int = Field(..., ge=1)
    user_id: int = Field(..., ge=1)


class DeleteAllCartRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    cart_ids: list[int] = Field(..., min_length=1)


__all__ = [
    "CartCreateRecord",
    "CreateCartRequest",
    "DeleteAllCartRequest",
    "DeleteCartRequest",
    "FindAllCarts",
]
