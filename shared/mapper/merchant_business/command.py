"""merchant_business command response mapping. `Create`/`Update` reuse the query-side `to_api_response_merchant_business` (identical shape), so only the delete-at envelope lives here. The `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` envelopes reuse the merchant mapper (`ApiResponse[None]`),, which borrows `merchantMapper.ToApiResponseMerchantDelete`/`All`."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_business import MerchantBusinessResponseDeleteAt
from shared.domain.response.responses import ApiResponse
from shared.mapper.merchant_business.mapper import (
    map_merchant_business_response_delete_at,
)


def to_api_response_merchant_business_delete_at(
    pb: Any,
) -> ApiResponse[MerchantBusinessResponseDeleteAt]:
    return ApiResponse[MerchantBusinessResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_merchant_business_response_delete_at(pb.data),
    )


__all__ = ["to_api_response_merchant_business_delete_at"]
