"""Order item request DTOs. `FindAllOrderItems` is built by the handler and never run through the validator, so it only clamps pagination (the service normalises again). `CreateOrderItemRecordRequest` / `UpdateOrderItemRecordRequest` Matches the expected `validator` tags; the handler maps any validation failure to the single `ErrGrpcInvalidID` (400). the tags use bare `required` (which rejects only the zero value, allowing negatives) plus `gt=0` / `gte=0`. tightens every numeric field to `> 0`: a non-positive id, quantity or price is always invalid downstream, and the handler collapses all of them to the same 400 either way."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class FindAllOrderItems(BaseModel):
    search: str = ""
    page: int = 1
    page_size: int = 10

    @model_validator(mode="after")
    def _clamp_pagination(self) -> FindAllOrderItems:
        if self.page <= 0:
            self.page = 1
        if self.page_size <= 0:
            self.page_size = 10
        if self.page_size > 100:
            self.page_size = 100
        return self


class CreateOrderItemRecordRequest(BaseModel):
    order_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    price: int = Field(..., gt=0)


class UpdateOrderItemRecordRequest(BaseModel):
    order_item_id: int = Field(..., gt=0)
    order_id: int = 0
    product_id: int = 0
    quantity: int = Field(..., gt=0)
    price: int = Field(..., gt=0)


__all__ = [
    "CreateOrderItemRecordRequest",
    "FindAllOrderItems",
    "UpdateOrderItemRecordRequest",
]
