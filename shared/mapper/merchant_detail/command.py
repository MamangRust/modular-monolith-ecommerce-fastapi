"""merchant_detail command response mapping. `Create`/`Update` reuse the query-side `to_api_response_merchant_detail` (identical shape), so only the command-only `DeleteAt` envelope lives here."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_detail import MerchantDetailResponseDeleteAt
from shared.domain.response.responses import ApiResponse
from shared.mapper.merchant_detail.mapper import (
    map_merchant_detail_response_delete_at,
)


def to_api_response_merchant_detail_delete_at(
    pb: Any,
) -> ApiResponse[MerchantDetailResponseDeleteAt]:
    return ApiResponse[MerchantDetailResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_merchant_detail_response_delete_at(pb.data),
    )


__all__ = [
    "to_api_response_merchant_detail_delete_at",
]
