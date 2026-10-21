"""Order request DTOs. Two families: - **internal records** (structs used by the service/repository, not user input): `FindAllOrder`, `FindAllOrderByMerchant`, the stats request records, `CreateOrderRecordRequest`, `UpdateOrderRecordRequest` — plain dataclasses; - **command DTOs** (validated): `CreateOrderRequest` / `UpdateOrderRequest` and their nested item DTOs. keeps the item models constraint-free to reproduce that. `shipping_address` reuses the shipping_address domain's constraint-free DTOs; the order-level validators supply the nested checks. `UpdateOrderRequest.order_id` is nullable 's `*int`."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, field_validator, model_validator

from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)


@dataclass
class FindAllOrder:
    """Service/cache request (`requests.FindAllOrder`)."""

    search: str
    page: int
    page_size: int


@dataclass
class FindAllOrderByMerchant:
    """Service/cache request (`requests.FindAllOrderByMerchant`)."""

    merchant_id: int
    search: str
    page: int
    page_size: int


@dataclass
class MonthTotalRevenue:
    year: int
    month: int


@dataclass
class MonthTotalRevenueOrder:
    order_id: int
    year: int
    month: int


@dataclass
class YearTotalRevenueOrder:
    order_id: int
    year: int


@dataclass
class MonthTotalRevenueMerchant:
    merchant_id: int
    year: int
    month: int


@dataclass
class YearTotalRevenueMerchant:
    merchant_id: int
    year: int


@dataclass
class MonthOrderMerchant:
    merchant_id: int
    year: int


@dataclass
class YearOrderMerchant:
    merchant_id: int
    year: int


@dataclass
class CreateOrderRecordRequest:
    """Repository create params (`db.CreateOrderParams`)."""

    merchant_id: int
    user_id: int
    total_price: int = 0


@dataclass
class UpdateOrderRecordRequest:
    """Repository update params (`requests.UpdateOrderRecordRequest`)."""

    order_id: int
    merchant_id: int
    user_id: int
    total_price: int


# ---- command DTOs (validated) ----


class CreateOrderItemRequest(BaseModel):
    """`requests.CreateOrderItemRequest` — tags exist but are never dived."""

    product_id: int = 0
    quantity: int = 0
    price: int = 0


class UpdateOrderItemRequest(BaseModel):
    """`requests.UpdateOrderItemRequest` — tags exist but are never dived."""

    order_item_id: int = 0
    product_id: int = 0
    quantity: int = 0
    price: int = 0


class CreateOrderRequest(BaseModel):
    """`requests.CreateOrderRequest` (nested shipping validated)."""

    merchant_id: int = 0
    user_id: int = 0
    total_price: int = 0
    items: list[CreateOrderItemRequest] = []
    shipping_address: CreateShippingAddressRequest = CreateShippingAddressRequest()

    @field_validator("merchant_id", "user_id", "total_price")
    @classmethod
    def _required_int(cls, value: int) -> int:
        if value == 0:
            raise ValueError("required")
        return value

    @field_validator("items")
    @classmethod
    def _required_items(
        cls, value: list[CreateOrderItemRequest]
    ) -> list[CreateOrderItemRequest]:
        if not value:
            raise ValueError("required")
        return value

    @model_validator(mode="after")
    def _validate_shipping(self) -> CreateOrderRequest:
        shipping = self.shipping_address
        if len(shipping.alamat) < 5:
            raise ValueError("alamat must be at least 5 characters")
        if not shipping.provinsi:
            raise ValueError("provinsi is required")
        if not shipping.kota:
            raise ValueError("kota is required")
        if not shipping.courier:
            raise ValueError("courier is required")
        if not shipping.shipping_method:
            raise ValueError("shipping_method is required")
        if shipping.shipping_cost == 0:
            raise ValueError("shipping_cost is required")
        if not shipping.negara:
            raise ValueError("negara is required")
        return self


class UpdateOrderRequest(BaseModel):
    """`requests.UpdateOrderRequest` (optional shipping, omitempty tags)."""

    order_id: int | None = None
    user_id: int = 0
    total_price: int = 0
    items: list[UpdateOrderItemRequest] = []
    shipping_address: UpdateShippingAddressRequest | None = None

    @field_validator("user_id", "total_price")
    @classmethod
    def _required_int(cls, value: int) -> int:
        if value == 0:
            raise ValueError("required")
        return value

    @field_validator("items")
    @classmethod
    def _required_items(
        cls, value: list[UpdateOrderItemRequest]
    ) -> list[UpdateOrderItemRequest]:
        if not value:
            raise ValueError("required")
        return value

    @model_validator(mode="after")
    def _validate_shipping(self) -> UpdateOrderRequest:
        shipping = self.shipping_address
        if shipping is not None and shipping.alamat and len(shipping.alamat) < 5:
            raise ValueError("alamat must be at least 5 characters")
        return self


__all__ = [
    "CreateOrderItemRequest",
    "CreateOrderRecordRequest",
    "CreateOrderRequest",
    "FindAllOrder",
    "FindAllOrderByMerchant",
    "MonthOrderMerchant",
    "MonthTotalRevenue",
    "MonthTotalRevenueMerchant",
    "MonthTotalRevenueOrder",
    "UpdateOrderItemRequest",
    "UpdateOrderRecordRequest",
    "UpdateOrderRequest",
    "YearOrderMerchant",
    "YearTotalRevenueMerchant",
    "YearTotalRevenueOrder",
]
