"""Order command-side REST mappers. duplicates the base `ToResponseOrder` / `ToResponsesOrder` / `ToApiResponseOrder` helpers across both the query and command mappers; keeps the single primitive in `mapper.py` and re-exposes it here to preserve the bundle shape."""

from __future__ import annotations

from typing import Any

from shared.domain.response.order import (
    OrderResponse,
    OrderResponseDeleteAt,
)
from shared.domain.response.order import (
    to_api_response_order_all as _to_all,
)
from shared.domain.response.order import (
    to_api_response_order_delete as _to_delete,
)
from shared.domain.response.responses import ApiResponse
from shared.mapper.order.mapper import (
    map_order_response,
    map_order_response_delete_at,
)


def to_response_order(pb: Any) -> OrderResponse:
    return map_order_response(pb)


def to_responses_order(orders: Any) -> list[OrderResponse]:
    return [map_order_response(order) for order in orders]


def to_api_response_order(pb: Any) -> ApiResponse[OrderResponse]:
    return ApiResponse[OrderResponse](
        status=pb.status,
        message=pb.message,
        data=map_order_response(pb.data),
    )


def to_response_order_delete_at(pb: Any) -> OrderResponseDeleteAt:
    return map_order_response_delete_at(pb)


def to_responses_order_delete_at(orders: Any) -> list[OrderResponseDeleteAt]:
    return [map_order_response_delete_at(order) for order in orders]


def to_api_response_order_delete_at(
    pb: Any,
) -> ApiResponse[OrderResponseDeleteAt]:
    return ApiResponse[OrderResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_order_response_delete_at(pb.data),
    )


def to_api_response_order_delete(pb: Any) -> ApiResponse[None]:
    return _to_delete(pb)


def to_api_response_order_all(pb: Any) -> ApiResponse[None]:
    return _to_all(pb)


__all__ = [
    "to_api_response_order",
    "to_api_response_order_all",
    "to_api_response_order_delete",
    "to_api_response_order_delete_at",
    "to_response_order",
    "to_response_order_delete_at",
    "to_responses_order",
    "to_responses_order_delete_at",
]
