"""Shipping address request DTOs. Unlike order_item, the shipping_address gRPC handler never calls `Validate` on these DTOs (the `validate` tags exist on the structs but are unused), so keeps them constraint-free: a create/update can only fail at the repository. `FindAllShippingAddress` is clamped to match the service's own normalisation."""

from __future__ import annotations

from pydantic import BaseModel, model_validator


class FindAllShippingAddress(BaseModel):
    search: str = ""
    page: int = 1
    page_size: int = 10

    @model_validator(mode="after")
    def _clamp_pagination(self) -> FindAllShippingAddress:
        if self.page <= 0:
            self.page = 1
        if self.page_size <= 0:
            self.page_size = 10
        if self.page_size > 100:
            self.page_size = 100
        return self


class CreateShippingAddressRequest(BaseModel):
    # declares `OrderID *int` (nullable); the handler always supplies it.
    order_id: int = 0
    alamat: str = ""
    provinsi: str = ""
    negara: str = ""
    kota: str = ""
    courier: str = ""
    shipping_method: str = ""
    shipping_cost: int = 0


class UpdateShippingAddressRequest(BaseModel):
    # declares `ShippingID *int` / `OrderID *int` (nullable). The order
    # service distinguishes "shipping id omitted" (fall back to FindByOrder)
    # from a supplied id, so them optional. Callers that always
    # have an id (the shipping handler, the order service after resolving it)
    # pass a concrete int.
    shipping_id: int | None = None
    order_id: int | None = None
    alamat: str = ""
    provinsi: str = ""
    negara: str = ""
    kota: str = ""
    courier: str = ""
    shipping_method: str = ""
    shipping_cost: int = 0


__all__ = [
    "CreateShippingAddressRequest",
    "FindAllShippingAddress",
    "UpdateShippingAddressRequest",
]
