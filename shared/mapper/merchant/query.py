"""Merchant query response mapping.

The proto already carries formatted `%Y-%m-%d %H:%M:%S` strings, so this layer
only shapes them into the REST envelopes — no reformatting."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant import (
    MerchantResponse,
    MerchantResponseDeleteAt,
)
from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
)
from shared.mapper.merchant.mapper import (
    map_merchant_response,
    map_merchant_response_delete_at,
    map_pagination_meta,
)


def to_api_response_merchant(pb: Any) -> ApiResponse[MerchantResponse]:
    return ApiResponse[MerchantResponse](
        status=pb.status,
        message=pb.message,
        data=map_merchant_response(pb.data),
    )


def to_api_responses_merchant(pb: Any) -> ApiResponse[list[MerchantResponse]]:
    return ApiResponse[list[MerchantResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_response(item) for item in pb.data],
    )


def to_api_response_pagination_merchant(
    pb: Any,
) -> APIResponsePagination[list[MerchantResponse]]:
    return APIResponsePagination[list[MerchantResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_merchant_delete_at(
    pb: Any,
) -> APIResponsePagination[list[MerchantResponseDeleteAt]]:
    return APIResponsePagination[list[MerchantResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_pagination_merchant",
    "to_api_response_pagination_merchant_delete_at",
    "to_api_response_merchant",
    "to_api_responses_merchant",
]
