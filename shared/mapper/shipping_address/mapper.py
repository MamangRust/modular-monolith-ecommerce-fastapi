"""Shipping address row/proto -> response DTO mapping. Two input shapes, one output: - row dataclasses — format the timestamps the way the handlers do (`%Y-%m-%d`) and truncate `shipping_cost` to an int; - proto messages — already-formatted strings, passed through unchanged. The REST shape drops `courier`, matching the `ShippingAddressResponse`. The default here is the query semantics; `command.py` carries the command override."""

from __future__ import annotations

from typing import Any

from pkg.database.schema.shipping_address import (
    CreateShippingAddressRow,
    GetShippingAddressActiveRow,
    GetShippingAddressByOrderIDRow,
    GetShippingAddressRow,
    GetShippingByIDRow,
    ShippingAddress,
    UpdateShippingAddressRow,
)
from shared.convert.convert import format_date
from shared.domain.response.shipping_address import (
    ShippingAddressResponse,
    ShippingAddressResponseDeleteAt,
)

ShippingAddressRow = (
    ShippingAddress
    | CreateShippingAddressRow
    | UpdateShippingAddressRow
    | GetShippingAddressRow
    | GetShippingByIDRow
    | GetShippingAddressByOrderIDRow
)
ShippingAddressDeleteAtRow = ShippingAddress | GetShippingAddressActiveRow


def to_shipping_address_response(row: ShippingAddressRow) -> ShippingAddressResponse:
    return ShippingAddressResponse(
        id=row.shipping_address_id,
        order_id=row.order_id,
        alamat=row.alamat,
        provinsi=row.provinsi,
        negara=row.negara,
        kota=row.kota,
        shipping_method=row.shipping_method,
        shipping_cost=int(row.shipping_cost),
        created_at=format_date(row.created_at),
        updated_at=format_date(row.updated_at),
    )


def to_shipping_address_response_delete_at(
    row: ShippingAddressDeleteAtRow,
) -> ShippingAddressResponseDeleteAt:
    return ShippingAddressResponseDeleteAt(
        id=row.shipping_address_id,
        order_id=row.order_id,
        alamat=row.alamat,
        provinsi=row.provinsi,
        negara=row.negara,
        kota=row.kota,
        shipping_method=row.shipping_method,
        shipping_cost=int(row.shipping_cost),
        created_at=format_date(row.created_at),
        updated_at=format_date(row.updated_at),
        deleted_at=format_date(row.deleted_at),
    )


def map_shipping_address_response(pb: Any) -> ShippingAddressResponse:
    return ShippingAddressResponse(
        id=int(pb.id),
        order_id=int(pb.order_id),
        alamat=pb.alamat,
        provinsi=pb.provinsi,
        negara=pb.negara,
        kota=pb.kota,
        shipping_method=pb.shippingMethod,
        shipping_cost=int(pb.shippingCost),
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_shipping_address_response_delete_at(
    pb: Any,
) -> ShippingAddressResponseDeleteAt:
    # Query semantics: an unset wrapper renders as `nil`/None.
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else None
    return ShippingAddressResponseDeleteAt(
        id=int(pb.id),
        order_id=int(pb.order_id),
        alamat=pb.alamat,
        provinsi=pb.provinsi,
        negara=pb.negara,
        kota=pb.kota,
        shipping_method=pb.shippingMethod,
        shipping_cost=int(pb.shippingCost),
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


__all__ = [
    "ShippingAddressDeleteAtRow",
    "ShippingAddressRow",
    "map_shipping_address_response",
    "map_shipping_address_response_delete_at",
    "to_shipping_address_response",
    "to_shipping_address_response_delete_at",
]
