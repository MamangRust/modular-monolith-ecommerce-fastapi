"""Banner response mapper."""

from __future__ import annotations

from shared.mapper.banner.command import (
    to_api_response_banner_all,
    to_api_response_banner_delete,
    to_api_response_banner_delete_at,
)
from shared.mapper.banner.mapper import (
    map_banner_response,
    map_banner_response_delete_at,
    to_banner_response,
    to_banner_response_delete_at,
)
from shared.mapper.banner.query import (
    map_pagination_meta,
    to_api_response_banner,
    to_api_response_pagination_banner,
    to_api_response_pagination_banner_delete_at,
    to_api_responses_banner,
)


class BannerQueryMapper:
    """Query-side mapper bundle (`BannerQueryResponseMapper`)."""

    map_pagination_meta = staticmethod(map_pagination_meta)
    to_api_response_banner = staticmethod(to_api_response_banner)
    to_api_responses_banner = staticmethod(to_api_responses_banner)
    to_api_response_pagination_banner = staticmethod(to_api_response_pagination_banner)
    to_api_response_pagination_banner_delete_at = staticmethod(
        to_api_response_pagination_banner_delete_at
    )


class BannerCommandMapper:
    """Command-side mapper bundle (`BannerCommandResponseMapper`)."""

    to_api_response_banner_delete_at = staticmethod(to_api_response_banner_delete_at)
    to_api_response_banner_delete = staticmethod(to_api_response_banner_delete)
    to_api_response_banner_all = staticmethod(to_api_response_banner_all)


class BannerResponseMapper:
    """Factory `NewBannerResponseMapper`."""

    def __init__(self) -> None:
        self._query = BannerQueryMapper()
        self._command = BannerCommandMapper()

    def query_mapper(self) -> BannerQueryMapper:
        return self._query

    def command_mapper(self) -> BannerCommandMapper:
        return self._command


def new_banner_response_mapper() -> BannerResponseMapper:
    return BannerResponseMapper()


__all__ = [
    "BannerCommandMapper",
    "BannerQueryMapper",
    "BannerResponseMapper",
    "map_banner_response",
    "map_banner_response_delete_at",
    "map_pagination_meta",
    "new_banner_response_mapper",
    "to_api_response_banner",
    "to_api_response_banner_all",
    "to_api_response_banner_delete",
    "to_api_response_banner_delete_at",
    "to_api_response_pagination_banner",
    "to_api_response_pagination_banner_delete_at",
    "to_api_responses_banner",
    "to_banner_response",
    "to_banner_response_delete_at",
]
