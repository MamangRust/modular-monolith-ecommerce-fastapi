"""Merchant command response mapping.

`Create`/`Update` reuse the query-side `to_api_response_merchant` (identical
shape), so only the command-only envelopes live here."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant import MerchantResponseDeleteAt
from shared.domain.response.responses import ApiResponse
from shared.mapper.merchant.mapper import map_merchant_response_delete_at


def to_api_response_merchant_delete_at(
    pb: Any,
) -> ApiResponse[MerchantResponseDeleteAt]:
    return ApiResponse[MerchantResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_merchant_response_delete_at(pb.data),
    )


def to_api_response_merchant_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_merchant_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


__all__ = [
    "to_api_response_merchant_all",
    "to_api_response_merchant_delete",
    "to_api_response_merchant_delete_at",
]
