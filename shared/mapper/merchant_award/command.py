"""merchant_award command response mapping. `Create`/`Update` reuse the query-side `to_api_response_merchant_award` (identical shape), so only the delete-at envelope lives here. The `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` envelopes reuse the merchant mapper (`ApiResponse[None]`),, which borrows `merchantMapper.ToApiResponseMerchantDelete`/`All`."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_award import MerchantAwardResponseDeleteAt
from shared.domain.response.responses import ApiResponse
from shared.mapper.merchant_award.mapper import map_merchant_award_response_delete_at


def to_api_response_merchant_award_delete_at(
    pb: Any,
) -> ApiResponse[MerchantAwardResponseDeleteAt]:
    return ApiResponse[MerchantAwardResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_merchant_award_response_delete_at(pb.data),
    )


__all__ = ["to_api_response_merchant_award_delete_at"]
