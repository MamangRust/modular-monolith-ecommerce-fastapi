"""Shipping address command response mapping. `Create`/`Update` reuse the query-side `to_api_response_shipping_address` (identical shape). The command mapper's `deleted_at` differs from the query one: always stores a pointer, so an absent wrapper renders as `""` (the `Trash`/`Restore` responses)."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
)
from shared.domain.response.shipping_address import (
    ShippingAddressResponseDeleteAt,
)
from shared.mapper.shipping_address.query import map_pagination_meta


def _map_delete_at_command(pb: Any) -> ShippingAddressResponseDeleteAt:
    # Command semantics: always sets the pointer, so "" when absent.
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
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


def to_api_response_shipping_address_delete_at(
    pb: Any,
) -> ApiResponse[ShippingAddressResponseDeleteAt]:
    return ApiResponse[ShippingAddressResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=_map_delete_at_command(pb.data),
    )


def to_api_response_shipping_address_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_shipping_address_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_pagination_shipping_address_delete_at(
    pb: Any,
) -> APIResponsePagination[list[ShippingAddressResponseDeleteAt]]:
    return APIResponsePagination[list[ShippingAddressResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[_map_delete_at_command(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_pagination_shipping_address_delete_at",
    "to_api_response_shipping_address_all",
    "to_api_response_shipping_address_delete",
    "to_api_response_shipping_address_delete_at",
]
