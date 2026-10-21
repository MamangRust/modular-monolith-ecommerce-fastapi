"""product query response mapping.

The proto already carries formatted strings, so this layer only shapes them into
the REST envelopes."""

from __future__ import annotations

from typing import Any

from shared.domain.response.product import (
    ProductResponse,
    ProductResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.mapper.product.mapper import (
    map_pagination_meta,
    map_product_response,
    map_product_response_delete_at,
)


def to_api_response_product(pb: Any) -> ApiResponse[ProductResponse]:
    return ApiResponse[ProductResponse](
        status=pb.status,
        message=pb.message,
        data=map_product_response(pb.data),
    )


def to_api_responses_products(
    pb: Any,
) -> ApiResponse[list[ProductResponse]]:
    return ApiResponse[list[ProductResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_product_response(item) for item in pb.data],
    )


def to_api_response_pagination_product(
    pb: Any,
) -> APIResponsePagination[list[ProductResponse]]:
    return APIResponsePagination[list[ProductResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_product_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_product_delete_at(
    pb: Any,
) -> APIResponsePagination[list[ProductResponseDeleteAt]]:
    return APIResponsePagination[list[ProductResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_product_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_pagination_product",
    "to_api_response_pagination_product_delete_at",
    "to_api_response_product",
    "to_api_responses_products",
]
