"""merchant_policy query response mapping.

The proto already carries formatted strings, so this layer only shapes them into
the REST envelopes."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_policy import (
    MerchantPoliciesResponse,
    MerchantPoliciesResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.mapper.merchant_policy.mapper import (
    map_merchant_policy_response,
    map_merchant_policy_response_delete_at,
    map_pagination_meta,
)


def to_api_response_merchant_policy(
    pb: Any,
) -> ApiResponse[MerchantPoliciesResponse]:
    return ApiResponse[MerchantPoliciesResponse](
        status=pb.status,
        message=pb.message,
        data=map_merchant_policy_response(pb.data),
    )


def to_api_responses_merchant_policies(
    pb: Any,
) -> ApiResponse[list[MerchantPoliciesResponse]]:
    return ApiResponse[list[MerchantPoliciesResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_policy_response(item) for item in pb.data],
    )


def to_api_response_pagination_merchant_policies(
    pb: Any,
) -> APIResponsePagination[list[MerchantPoliciesResponse]]:
    return APIResponsePagination[list[MerchantPoliciesResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_policy_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_merchant_policies_delete_at(
    pb: Any,
) -> APIResponsePagination[list[MerchantPoliciesResponseDeleteAt]]:
    return APIResponsePagination[list[MerchantPoliciesResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_policy_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_merchant_policy",
    "to_api_response_pagination_merchant_policies",
    "to_api_response_pagination_merchant_policies_delete_at",
    "to_api_responses_merchant_policies",
]
