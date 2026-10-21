"""Cart query-side REST mappers."""

from __future__ import annotations

from typing import Any

from shared.domain.response.cart import CartResponse
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.mapper.cart.mapper import map_cart_response, map_pagination_meta


def to_api_response_cart(pb: Any) -> ApiResponse[CartResponse]:
    return ApiResponse[CartResponse](
        status=pb.status,
        message=pb.message,
        data=map_cart_response(pb.data),
    )


def to_api_responses_carts(pb: Any) -> ApiResponse[list[CartResponse]]:
    return ApiResponse[list[CartResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_cart_response(row) for row in pb.data],
    )


def to_api_response_pagination_cart(
    pb: Any,
) -> APIResponsePagination[list[CartResponse]]:
    return APIResponsePagination[list[CartResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_cart_response(row) for row in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_cart",
    "to_api_response_pagination_cart",
    "to_api_responses_carts",
]
