"""Banner command response mapping.

`Create`/`Update` reuse the query-side `to_api_response_banner` (identical
shape), so only the command-only envelopes live here."""

from __future__ import annotations

from typing import Any

from shared.domain.response.banner import BannerResponseDeleteAt
from shared.domain.response.responses import ApiResponse
from shared.mapper.banner.mapper import map_banner_response_delete_at


def to_api_response_banner_delete_at(
    pb: Any,
) -> ApiResponse[BannerResponseDeleteAt]:
    return ApiResponse[BannerResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_banner_response_delete_at(pb.data),
    )


def to_api_response_banner_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_banner_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


__all__ = [
    "to_api_response_banner_all",
    "to_api_response_banner_delete",
    "to_api_response_banner_delete_at",
]
