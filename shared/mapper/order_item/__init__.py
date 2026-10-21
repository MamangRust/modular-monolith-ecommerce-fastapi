"""Order item response mapper. `OrderItemResponseMapper` bundles the query and command mappers, `NewOrderItemResponseMapper`."""

from __future__ import annotations

from shared.mapper.order_item.command import (
    to_api_response_order_item_all,
    to_api_response_order_item_delete,
    to_api_response_pagination_order_item_delete_at,
)
from shared.mapper.order_item.mapper import (
    map_order_item_response,
    map_order_item_response_delete_at,
    to_order_item_response,
    to_order_item_response_delete_at,
)
from shared.mapper.order_item.query import (
    map_pagination_meta,
    to_api_response_order_item,
    to_api_response_pagination_order_item,
    to_api_responses_order_item,
)


class OrderItemQueryMapper:
    """Query-side mapper bundle (`OrderItemQueryResponseMapper`)."""

    map_pagination_meta = staticmethod(map_pagination_meta)
    to_api_response_order_item = staticmethod(to_api_response_order_item)
    to_api_responses_order_item = staticmethod(to_api_responses_order_item)
    to_api_response_pagination_order_item = staticmethod(
        to_api_response_pagination_order_item
    )
    to_api_response_pagination_order_item_delete_at = staticmethod(
        to_api_response_pagination_order_item_delete_at
    )


class OrderItemCommandMapper:
    """Command-side mapper bundle (`OrderItemCommandResponseMapper`)."""

    to_api_response_order_item = staticmethod(to_api_response_order_item)
    to_api_response_order_item_delete = staticmethod(
        to_api_response_order_item_delete
    )
    to_api_response_order_item_all = staticmethod(to_api_response_order_item_all)
    to_api_response_pagination_order_item_delete_at = staticmethod(
        to_api_response_pagination_order_item_delete_at
    )


class OrderItemResponseMapper:
    """Factory `NewOrderItemResponseMapper`."""

    def __init__(self) -> None:
        self._query = OrderItemQueryMapper()
        self._command = OrderItemCommandMapper()

    def query_mapper(self) -> OrderItemQueryMapper:
        return self._query

    def command_mapper(self) -> OrderItemCommandMapper:
        return self._command


def new_order_item_response_mapper() -> OrderItemResponseMapper:
    return OrderItemResponseMapper()


__all__ = [
    "OrderItemCommandMapper",
    "OrderItemQueryMapper",
    "OrderItemResponseMapper",
    "map_order_item_response",
    "map_order_item_response_delete_at",
    "map_pagination_meta",
    "new_order_item_response_mapper",
    "to_api_response_order_item",
    "to_api_response_order_item_all",
    "to_api_response_order_item_delete",
    "to_api_response_pagination_order_item",
    "to_api_response_pagination_order_item_delete_at",
    "to_api_responses_order_item",
    "to_order_item_response",
    "to_order_item_response_delete_at",
]
