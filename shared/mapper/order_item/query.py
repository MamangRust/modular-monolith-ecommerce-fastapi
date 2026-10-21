"""Order item query response mapping.

The proto already carries formatted strings, so this layer only shapes them
into the REST envelopes — no reformatting."""

from __future__ import annotations

from typing import Any

from shared.domain.response.order_item import (
    OrderItemResponse,
    OrderItemResponseDeleteAt,
)
from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)
from shared.mapper.order_item.mapper import (
    map_order_item_response,
    map_order_item_response_delete_at,
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


def to_api_response_order_item(pb: Any) -> ApiResponse[OrderItemResponse]:
    return ApiResponse[OrderItemResponse](
        status=pb.status,
        message=pb.message,
        data=map_order_item_response(pb.data),
    )


def to_api_responses_order_item(pb: Any) -> ApiResponse[list[OrderItemResponse]]:
    return ApiResponse[list[OrderItemResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_order_item_response(item) for item in pb.data],
    )


def to_api_response_pagination_order_item(
    pb: Any,
) -> APIResponsePagination[list[OrderItemResponse]]:
    return APIResponsePagination[list[OrderItemResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_order_item_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


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
    "map_pagination_meta",
    "to_api_response_order_item",
    "to_api_response_pagination_order_item",
    "to_api_response_pagination_order_item_delete_at",
    "to_api_responses_order_item",
]
