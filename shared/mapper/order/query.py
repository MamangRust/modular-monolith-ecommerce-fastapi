"""Order query-side REST mappers."""

from __future__ import annotations

from typing import Any

from shared.domain.response.order import (
    OrderResponse,
    OrderResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.mapper.order.mapper import (
    map_order_response,
    map_order_response_delete_at,
    map_pagination_meta,
)


def to_api_response_order(pb: Any) -> ApiResponse[OrderResponse]:
    return ApiResponse[OrderResponse](
        status=pb.status,
        message=pb.message,
        data=map_order_response(pb.data),
    )


def to_api_responses_orders(pb: Any) -> ApiResponse[list[OrderResponse]]:
    return ApiResponse[list[OrderResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_order_response(row) for row in pb.data],
    )


def to_api_response_pagination_order(
    pb: Any,
) -> APIResponsePagination[list[OrderResponse]]:
    return APIResponsePagination[list[OrderResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_order_response(row) for row in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_order_delete_at(
    pb: Any,
) -> APIResponsePagination[list[OrderResponseDeleteAt]]:
    return APIResponsePagination[list[OrderResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_order_response_delete_at(row) for row in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_order",
    "to_api_response_pagination_order",
    "to_api_response_pagination_order_delete_at",
    "to_api_responses_orders",
]
