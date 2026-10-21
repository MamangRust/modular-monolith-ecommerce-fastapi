"""merchant_business query response mapping.

The proto already carries formatted strings, so this layer only shapes them into
the REST envelopes."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_business import (
    MerchantBusinessResponse,
    MerchantBusinessResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.mapper.merchant_business.mapper import (
    map_merchant_business_response,
    map_merchant_business_response_delete_at,
    map_pagination_meta,
)


def to_api_response_merchant_business(
    pb: Any,
) -> ApiResponse[MerchantBusinessResponse]:
    return ApiResponse[MerchantBusinessResponse](
        status=pb.status,
        message=pb.message,
        data=map_merchant_business_response(pb.data),
    )


def to_api_responses_merchant_business(
    pb: Any,
) -> ApiResponse[list[MerchantBusinessResponse]]:
    return ApiResponse[list[MerchantBusinessResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_business_response(item) for item in pb.data],
    )


def to_api_response_pagination_merchant_business(
    pb: Any,
) -> APIResponsePagination[list[MerchantBusinessResponse]]:
    return APIResponsePagination[list[MerchantBusinessResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_business_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_merchant_business_delete_at(
    pb: Any,
) -> APIResponsePagination[list[MerchantBusinessResponseDeleteAt]]:
    return APIResponsePagination[list[MerchantBusinessResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_business_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_merchant_business",
    "to_api_response_pagination_merchant_business",
    "to_api_response_pagination_merchant_business_delete_at",
    "to_api_responses_merchant_business",
]
