"""Row types for the shipping_addresses table. Timestamps are `pgtype.Timestamp` in and the shipping handlers format them with the date-only layout `2006-01-02` (`%Y-%m-%d`) — same as category, not the millisecond layout used by banner/order_item."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ShippingAddress:

    shipping_address_id: int
    order_id: int
    alamat: str
    provinsi: str
    negara: str
    kota: str
    courier: str
    shipping_method: str
    shipping_cost: float
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> ShippingAddress:
        return cls(
            shipping_address_id=row["shipping_address_id"],
            order_id=row["order_id"],
            alamat=row["alamat"],
            provinsi=row["provinsi"],
            negara=row["negara"],
            kota=row["kota"],
            courier=row["courier"],
            shipping_method=row["shipping_method"],
            shipping_cost=row["shipping_cost"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateShippingAddressRow:
    shipping_address_id: int
    order_id: int
    alamat: str
    provinsi: str
    negara: str
    kota: str
    courier: str
    shipping_method: str
    shipping_cost: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateShippingAddressRow:
        return cls(
            shipping_address_id=row["shipping_address_id"],
            order_id=row["order_id"],
            alamat=row["alamat"],
            provinsi=row["provinsi"],
            negara=row["negara"],
            kota=row["kota"],
            courier=row["courier"],
            shipping_method=row["shipping_method"],
            shipping_cost=row["shipping_cost"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateShippingAddressRow = CreateShippingAddressRow


@dataclass
class GetShippingAddressRow:
    """`FindAll` projection with a window total count."""

    shipping_address_id: int
    order_id: int
    alamat: str
    provinsi: str
    negara: str
    kota: str
    courier: str
    shipping_method: str
    shipping_cost: float
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetShippingAddressRow:
        return cls(
            shipping_address_id=row["shipping_address_id"],
            order_id=row["order_id"],
            alamat=row["alamat"],
            provinsi=row["provinsi"],
            negara=row["negara"],
            kota=row["kota"],
            courier=row["courier"],
            shipping_method=row["shipping_method"],
            shipping_cost=row["shipping_cost"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetShippingAddressActiveRow:
    shipping_address_id: int
    order_id: int
    alamat: str
    provinsi: str
    negara: str
    kota: str
    courier: str
    shipping_method: str
    shipping_cost: float
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetShippingAddressActiveRow:
        return cls(
            shipping_address_id=row["shipping_address_id"],
            order_id=row["order_id"],
            alamat=row["alamat"],
            provinsi=row["provinsi"],
            negara=row["negara"],
            kota=row["kota"],
            courier=row["courier"],
            shipping_method=row["shipping_method"],
            shipping_cost=row["shipping_cost"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetShippingAddressTrashedRow = GetShippingAddressActiveRow


@dataclass
class GetShippingByIDRow:
    """`FindByID` projection — no `deleted_at`, no total count."""

    shipping_address_id: int
    order_id: int
    alamat: str
    provinsi: str
    negara: str
    kota: str
    courier: str
    shipping_method: str
    shipping_cost: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetShippingByIDRow:
        return cls(
            shipping_address_id=row["shipping_address_id"],
            order_id=row["order_id"],
            alamat=row["alamat"],
            provinsi=row["provinsi"],
            negara=row["negara"],
            kota=row["kota"],
            courier=row["courier"],
            shipping_method=row["shipping_method"],
            shipping_cost=row["shipping_cost"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class GetShippingAddressByOrderIDRow:
    """`FindByOrder` projection — same shape as `GetShippingByIDRow`."""

    shipping_address_id: int
    order_id: int
    alamat: str
    provinsi: str
    negara: str
    kota: str
    courier: str
    shipping_method: str
    shipping_cost: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetShippingAddressByOrderIDRow:
        return cls(
            shipping_address_id=row["shipping_address_id"],
            order_id=row["order_id"],
            alamat=row["alamat"],
            provinsi=row["provinsi"],
            negara=row["negara"],
            kota=row["kota"],
            courier=row["courier"],
            shipping_method=row["shipping_method"],
            shipping_cost=row["shipping_cost"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


__all__ = [
    "CreateShippingAddressRow",
    "GetShippingAddressActiveRow",
    "GetShippingAddressByOrderIDRow",
    "GetShippingAddressRow",
    "GetShippingAddressTrashedRow",
    "GetShippingByIDRow",
    "ShippingAddress",
    "UpdateShippingAddressRow",
]
