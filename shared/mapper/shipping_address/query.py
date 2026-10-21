"""Shipping address query response mapping.

The proto already carries formatted strings, so this layer only shapes them
into the REST envelopes — no reformatting."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)
from shared.domain.response.shipping_address import (
    ShippingAddressResponse,
    ShippingAddressResponseDeleteAt,
)
from shared.mapper.shipping_address.mapper import (
    map_shipping_address_response,
    map_shipping_address_response_delete_at,
)


def map_pagination_meta(meta: Any) -> PaginationMeta:
    if meta is None:
        return PaginationMeta()
    return PaginationMeta(
        current_page=int(meta.current_page),
        page_size=int(meta.page_size),
        total_pages=int(meta.total_pages),
        total_records=int(meta.total_records),
    )


def to_api_response_shipping_address(
    pb: Any,
) -> ApiResponse[ShippingAddressResponse]:
    return ApiResponse[ShippingAddressResponse](
        status=pb.status,
        message=pb.message,
        data=map_shipping_address_response(pb.data),
    )


def to_api_responses_shipping_address(
    pb: Any,
) -> ApiResponse[list[ShippingAddressResponse]]:
    return ApiResponse[list[ShippingAddressResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_shipping_address_response(item) for item in pb.data],
    )


def to_api_response_pagination_shipping_address(
    pb: Any,
) -> APIResponsePagination[list[ShippingAddressResponse]]:
    return APIResponsePagination[list[ShippingAddressResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_shipping_address_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_shipping_address_delete_at(
    pb: Any,
) -> APIResponsePagination[list[ShippingAddressResponseDeleteAt]]:
    return APIResponsePagination[list[ShippingAddressResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_shipping_address_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "map_pagination_meta",
    "to_api_response_pagination_shipping_address",
    "to_api_response_pagination_shipping_address_delete_at",
    "to_api_response_shipping_address",
    "to_api_responses_shipping_address",
]
