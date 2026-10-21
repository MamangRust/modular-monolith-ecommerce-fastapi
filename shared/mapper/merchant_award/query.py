"""merchant_award query response mapping.

The proto already carries formatted date/timestamp strings, so this layer only
shapes them into the REST envelopes."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_award import (
    MerchantAwardResponse,
    MerchantAwardResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.mapper.merchant_award.mapper import (
    map_merchant_award_response,
    map_merchant_award_response_delete_at,
    map_pagination_meta,
)


def to_api_response_merchant_award(
    pb: Any,
) -> ApiResponse[MerchantAwardResponse]:
    return ApiResponse[MerchantAwardResponse](
        status=pb.status,
        message=pb.message,
        data=map_merchant_award_response(pb.data),
    )


def to_api_responses_merchant_award(
    pb: Any,
) -> ApiResponse[list[MerchantAwardResponse]]:
    return ApiResponse[list[MerchantAwardResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_award_response(item) for item in pb.data],
    )


def to_api_response_pagination_merchant_award(
    pb: Any,
) -> APIResponsePagination[list[MerchantAwardResponse]]:
    return APIResponsePagination[list[MerchantAwardResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_award_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_merchant_award_delete_at(
    pb: Any,
) -> APIResponsePagination[list[MerchantAwardResponseDeleteAt]]:
    return APIResponsePagination[list[MerchantAwardResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_award_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_merchant_award",
    "to_api_response_pagination_merchant_award",
    "to_api_response_pagination_merchant_award_delete_at",
    "to_api_responses_merchant_award",
]
