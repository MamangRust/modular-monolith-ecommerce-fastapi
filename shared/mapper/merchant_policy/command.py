"""merchant_policy command response mapping. `Create`/`Update` reuse the query-side `to_api_response_merchant_policy` (identical shape), so only the delete-at envelope lives here. The `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` envelopes reuse the merchant mapper (`ApiResponse[None]`),, which borrows `merchantMapper.ToApiResponseMerchantDelete`/`All`."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_policy import MerchantPoliciesResponseDeleteAt
from shared.domain.response.responses import ApiResponse
from shared.mapper.merchant_policy.mapper import (
    map_merchant_policy_response_delete_at,
)


def to_api_response_merchant_policy_delete_at(
    pb: Any,
) -> ApiResponse[MerchantPoliciesResponseDeleteAt]:
    return ApiResponse[MerchantPoliciesResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_merchant_policy_response_delete_at(pb.data),
    )


__all__ = ["to_api_response_merchant_policy_delete_at"]
