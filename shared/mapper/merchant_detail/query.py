"""merchant_detail query response mapping.

The proto already carries formatted `%Y-%m-%d %H:%M:%S.mmm` strings, so this
layer only shapes them into the REST envelopes."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_detail import (
    MerchantDetailResponse,
    MerchantDetailResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.mapper.merchant_detail.mapper import (
    map_merchant_detail_response,
    map_merchant_detail_response_delete_at,
    map_merchant_detail_response_relation,
    map_pagination_meta,
)


def to_api_response_merchant_detail(
    pb: Any,
) -> ApiResponse[MerchantDetailResponse]:
    return ApiResponse[MerchantDetailResponse](
        status=pb.status,
        message=pb.message,
        data=map_merchant_detail_response(pb.data),
    )


def to_api_response_merchant_detail_relation(
    pb: Any,
) -> ApiResponse[MerchantDetailResponse]:
    return ApiResponse[MerchantDetailResponse](
        status=pb.status,
        message=pb.message,
        data=map_merchant_detail_response_relation(pb.data),
    )


def to_api_responses_merchant_detail(
    pb: Any,
) -> ApiResponse[list[MerchantDetailResponse]]:
    return ApiResponse[list[MerchantDetailResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_detail_response_relation(item) for item in pb.data],
    )


def to_api_response_pagination_merchant_detail(
    pb: Any,
) -> APIResponsePagination[list[MerchantDetailResponse]]:
    return APIResponsePagination[list[MerchantDetailResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_detail_response_relation(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_merchant_detail_delete_at(
    pb: Any,
) -> APIResponsePagination[list[MerchantDetailResponseDeleteAt]]:
    return APIResponsePagination[list[MerchantDetailResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_detail_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_merchant_detail",
    "to_api_response_merchant_detail_relation",
    "to_api_response_pagination_merchant_detail",
    "to_api_response_pagination_merchant_detail_delete_at",
    "to_api_responses_merchant_detail",
]
