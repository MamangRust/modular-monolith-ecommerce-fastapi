"""merchant_social_link proto -> response DTO mapping.

The command mapper copies only `id`/`merchant_detail_id`/`platform`/`url` (the
query mapper additionally carries timestamps, but the gateway only registers
the command routes)."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_detail import MerchantSocialLinkResponse
from shared.domain.response.responses import ApiResponse


def map_merchant_social_link(pb: Any) -> MerchantSocialLinkResponse:
    return MerchantSocialLinkResponse(
        id=int(pb.id),
        merchant_detail_id=int(pb.merchant_detail_id),
        platform=pb.platform,
        url=pb.url,
    )


def to_api_response_merchant_social_link(
    pb: Any,
) -> ApiResponse[MerchantSocialLinkResponse]:
    return ApiResponse[MerchantSocialLinkResponse](
        status=pb.status,
        message=pb.message,
        data=map_merchant_social_link(pb.data),
    )


__all__ = [
    "map_merchant_social_link",
    "to_api_response_merchant_social_link",
]
