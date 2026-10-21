"""Shipping address response DTOs. The REST shape **drops `courier`** even though the proto carries it: `ShippingAddressResponse` has no courier field. `shipping_cost` is an `int` on REST (the gRPC handler already truncated the float64). Timestamps are already formatted by the gRPC handlers, so the mapper passes them through unchanged."""

from __future__ import annotations

from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
)


@dataclass
class ShippingAddressResponse:
    id: int
    order_id: int
    alamat: str
    provinsi: str
    negara: str
    kota: str
    shipping_method: str
    shipping_cost: int
    created_at: str
    updated_at: str


@dataclass
class ShippingAddressResponseDeleteAt:
    id: int
    order_id: int
    alamat: str
    provinsi: str
    negara: str
    kota: str
    shipping_method: str
    shipping_cost: int
    created_at: str
    updated_at: str
    deleted_at: str | None = None


# API response wrappers (kept close to the names) ----

ShippingAddressResponseApi = ApiResponse[ShippingAddressResponse]
ShippingAddressesResponse = ApiResponse[list[ShippingAddressResponse]]
ShippingAddressResponseDelete = ApiResponse[None]
ShippingAddressResponseAll = ApiResponse[None]
ShippingAddressResponsePagination = APIResponsePagination[
    list[ShippingAddressResponse]
]
ShippingAddressResponsePaginationDeleteAt = APIResponsePagination[
    list[ShippingAddressResponseDeleteAt]
]


__all__ = [
    "ShippingAddressResponse",
    "ShippingAddressResponseAll",
    "ShippingAddressResponseApi",
    "ShippingAddressResponseDelete",
    "ShippingAddressResponseDeleteAt",
    "ShippingAddressResponsePagination",
    "ShippingAddressResponsePaginationDeleteAt",
    "ShippingAddressesResponse",
]
