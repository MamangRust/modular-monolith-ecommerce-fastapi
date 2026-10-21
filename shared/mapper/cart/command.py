"""Cart command-side REST mappers."""

from __future__ import annotations

from typing import Any

from shared.domain.response.cart import CartResponse
from shared.domain.response.responses import ApiResponse
from shared.mapper.cart.mapper import map_cart_response


def to_api_response_cart(pb: Any) -> ApiResponse[CartResponse]:
    return ApiResponse[CartResponse](
        status=pb.status,
        message=pb.message,
        data=map_cart_response(pb.data),
    )


def to_api_response_cart_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message)


def to_api_response_cart_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message)


__all__ = [
    "to_api_response_cart",
    "to_api_response_cart_all",
    "to_api_response_cart_delete",
]
