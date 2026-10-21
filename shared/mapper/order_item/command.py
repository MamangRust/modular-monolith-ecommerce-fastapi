"""Order item command response mapping.

`Create`/`Update` reuse the query-side `to_api_response_order_item` (identical
shape), so only the command-only envelopes live here."""

from __future__ import annotations

from typing import Any

from shared.domain.response.order_item import OrderItemResponseDeleteAt
from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
)
from shared.mapper.order_item.mapper import map_order_item_response_delete_at
from shared.mapper.order_item.query import map_pagination_meta


def to_api_response_order_item_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_order_item_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_pagination_order_item_delete_at(
    pb: Any,
) -> APIResponsePagination[list[OrderItemResponseDeleteAt]]:
    return APIResponsePagination[list[OrderItemResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_order_item_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_order_item_all",
    "to_api_response_order_item_delete",
    "to_api_response_pagination_order_item_delete_at",
]
