"""Shipping address response mapper. `ShippingAddressResponseMapper` bundles the query and command mappers, matching the `NewShippingAddressResponseMapper`."""

from __future__ import annotations

from shared.mapper.shipping_address.command import (
    to_api_response_pagination_shipping_address_delete_at,
    to_api_response_shipping_address_all,
    to_api_response_shipping_address_delete,
    to_api_response_shipping_address_delete_at,
)
from shared.mapper.shipping_address.mapper import (
    map_shipping_address_response,
    map_shipping_address_response_delete_at,
    to_shipping_address_response,
    to_shipping_address_response_delete_at,
)
from shared.mapper.shipping_address.query import (
    map_pagination_meta,
    to_api_response_pagination_shipping_address,
    to_api_response_shipping_address,
    to_api_responses_shipping_address,
)


class ShippingAddressQueryMapper:
    """Query-side mapper bundle (`ShippingAddressQueryResponseMapper`)."""

    map_pagination_meta = staticmethod(map_pagination_meta)
    to_api_response_shipping_address = staticmethod(to_api_response_shipping_address)
    to_api_responses_shipping_address = staticmethod(
        to_api_responses_shipping_address
    )
    to_api_response_pagination_shipping_address = staticmethod(
        to_api_response_pagination_shipping_address
    )
    to_api_response_pagination_shipping_address_delete_at = staticmethod(
        to_api_response_pagination_shipping_address_delete_at
    )


class ShippingAddressCommandMapper:
    """Command-side mapper bundle (`ShippingAddressCommandResponseMapper`)."""

    to_api_response_shipping_address = staticmethod(to_api_response_shipping_address)
    to_api_response_shipping_address_delete = staticmethod(
        to_api_response_shipping_address_delete
    )
    to_api_response_shipping_address_delete_at = staticmethod(
        to_api_response_shipping_address_delete_at
    )
    to_api_response_shipping_address_all = staticmethod(
        to_api_response_shipping_address_all
    )
    to_api_response_pagination_shipping_address_delete_at = staticmethod(
        to_api_response_pagination_shipping_address_delete_at
    )


class ShippingAddressResponseMapper:
    """Factory `NewShippingAddressResponseMapper`."""

    def __init__(self) -> None:
        self._query = ShippingAddressQueryMapper()
        self._command = ShippingAddressCommandMapper()

    def query_mapper(self) -> ShippingAddressQueryMapper:
        return self._query

    def command_mapper(self) -> ShippingAddressCommandMapper:
        return self._command


def new_shipping_address_response_mapper() -> ShippingAddressResponseMapper:
    return ShippingAddressResponseMapper()


__all__ = [
    "ShippingAddressCommandMapper",
    "ShippingAddressQueryMapper",
    "ShippingAddressResponseMapper",
    "map_pagination_meta",
    "map_shipping_address_response",
    "map_shipping_address_response_delete_at",
    "new_shipping_address_response_mapper",
    "to_api_response_pagination_shipping_address",
    "to_api_response_pagination_shipping_address_delete_at",
    "to_api_response_shipping_address",
    "to_api_response_shipping_address_all",
    "to_api_response_shipping_address_delete",
    "to_api_response_shipping_address_delete_at",
    "to_api_responses_shipping_address",
    "to_shipping_address_response",
    "to_shipping_address_response_delete_at",
]
