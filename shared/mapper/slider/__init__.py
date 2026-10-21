"""Slider response mapper."""

from __future__ import annotations

from shared.mapper.slider.command import (
    to_api_response_slider_all,
    to_api_response_slider_delete,
    to_api_response_slider_delete_at,
)
from shared.mapper.slider.mapper import (
    map_slider_response,
    map_slider_response_delete_at,
    to_slider_response,
    to_slider_response_delete_at,
)
from shared.mapper.slider.query import (
    map_pagination_meta,
    to_api_response_pagination_slider,
    to_api_response_pagination_slider_delete_at,
    to_api_response_slider,
    to_api_responses_slider,
)


class SliderQueryMapper:
    """Query-side mapper bundle (`SliderQueryResponseMapper`)."""

    map_pagination_meta = staticmethod(map_pagination_meta)
    to_api_response_slider = staticmethod(to_api_response_slider)
    to_api_responses_slider = staticmethod(to_api_responses_slider)
    to_api_response_pagination_slider = staticmethod(to_api_response_pagination_slider)
    to_api_response_pagination_slider_delete_at = staticmethod(
        to_api_response_pagination_slider_delete_at
    )


class SliderCommandMapper:
    """Command-side mapper bundle (`SliderCommandResponseMapper`)."""

    to_api_response_slider_delete_at = staticmethod(to_api_response_slider_delete_at)
    to_api_response_slider_delete = staticmethod(to_api_response_slider_delete)
    to_api_response_slider_all = staticmethod(to_api_response_slider_all)


class SliderResponseMapper:
    """Factory `NewSliderResponseMapper`."""

    def __init__(self) -> None:
        self._query = SliderQueryMapper()
        self._command = SliderCommandMapper()

    def query_mapper(self) -> SliderQueryMapper:
        return self._query

    def command_mapper(self) -> SliderCommandMapper:
        return self._command


def new_slider_response_mapper() -> SliderResponseMapper:
    return SliderResponseMapper()


__all__ = [
    "SliderCommandMapper",
    "SliderQueryMapper",
    "SliderResponseMapper",
    "map_slider_response",
    "map_slider_response_delete_at",
    "map_pagination_meta",
    "new_slider_response_mapper",
    "to_api_response_pagination_slider",
    "to_api_response_pagination_slider_delete_at",
    "to_api_response_slider",
    "to_api_response_slider_all",
    "to_api_response_slider_delete",
    "to_api_response_slider_delete_at",
    "to_api_responses_slider",
    "to_slider_response",
    "to_slider_response_delete_at",
]
