"""Slider command response mapping.

`Create`/`Update` reuse the query-side `to_api_response_slider` (identical
shape), so only the command-only envelopes live here."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import ApiResponse
from shared.domain.response.slider import SliderResponseDeleteAt
from shared.mapper.slider.mapper import map_slider_response_delete_at


def to_api_response_slider_delete_at(
    pb: Any,
) -> ApiResponse[SliderResponseDeleteAt]:
    return ApiResponse[SliderResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_slider_response_delete_at(pb.data),
    )


def to_api_response_slider_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_slider_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


__all__ = [
    "to_api_response_slider_all",
    "to_api_response_slider_delete",
    "to_api_response_slider_delete_at",
]
