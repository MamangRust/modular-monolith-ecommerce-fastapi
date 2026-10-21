"""Category response mapper. `CategoryQueryMapper` embeds the command mapper, matching the `categoryQueryResponseMapper` embedding `CategoryCommandResponseMapper`."""

from __future__ import annotations

from shared.mapper.category.command import (
    to_api_response_category_all,
    to_api_response_category_delete,
    to_api_response_category_delete_at,
    to_api_response_pagination_category_delete_at,
)
from shared.mapper.category.mapper import (
    map_category_response,
    map_category_response_delete_at,
    to_category_response,
    to_category_response_delete_at,
)
from shared.mapper.category.query import (
    map_pagination_meta,
    to_api_response_category,
    to_api_response_pagination_category,
    to_api_responses_category,
)
from shared.mapper.category.stats import (
    map_categories_monthly_total_price,
    map_categories_monthly_total_prices,
    map_categories_yearly_total_price,
    map_categories_yearly_total_prices,
    map_category_month_price,
    map_category_month_prices,
    map_category_year_price,
    map_category_year_prices,
    to_api_response_category_month_price,
    to_api_response_category_monthly_total_price,
    to_api_response_category_year_price,
    to_api_response_category_yearly_total_price,
)


class CategoryQueryMapper:
    """Query-side mapper bundle (`CategoryQueryResponseMapper`)."""

    map_pagination_meta = staticmethod(map_pagination_meta)
    to_api_response_category = staticmethod(to_api_response_category)
    to_api_responses_category = staticmethod(to_api_responses_category)
    to_api_response_pagination_category = staticmethod(
        to_api_response_pagination_category
    )
    to_api_response_category_delete_at = staticmethod(
        to_api_response_category_delete_at
    )
    to_api_response_pagination_category_delete_at = staticmethod(
        to_api_response_pagination_category_delete_at
    )


class CategoryCommandMapper:
    """Command-side mapper bundle (`CategoryCommandResponseMapper`)."""

    to_api_response_category_delete_at = staticmethod(
        to_api_response_category_delete_at
    )
    to_api_response_category_delete = staticmethod(to_api_response_category_delete)
    to_api_response_category_all = staticmethod(to_api_response_category_all)
    to_api_response_pagination_category_delete_at = staticmethod(
        to_api_response_pagination_category_delete_at
    )


class CategoryStatsMapper:
    """Stats-side mapper bundle (`CategoryStatsResponseMapper`)."""

    to_api_response_category_month_price = staticmethod(
        to_api_response_category_month_price
    )
    to_api_response_category_year_price = staticmethod(
        to_api_response_category_year_price
    )
    to_api_response_category_monthly_total_price = staticmethod(
        to_api_response_category_monthly_total_price
    )
    to_api_response_category_yearly_total_price = staticmethod(
        to_api_response_category_yearly_total_price
    )


class CategoryResponseMapper:
    """Factory `NewCategoryResponseMapper`."""

    def __init__(self) -> None:
        self._query = CategoryQueryMapper()
        self._command = CategoryCommandMapper()
        self._stats = CategoryStatsMapper()

    def query_mapper(self) -> CategoryQueryMapper:
        return self._query

    def command_mapper(self) -> CategoryCommandMapper:
        return self._command

    def stats_mapper(self) -> CategoryStatsMapper:
        return self._stats


def new_category_response_mapper() -> CategoryResponseMapper:
    return CategoryResponseMapper()


__all__ = [
    "CategoryCommandMapper",
    "CategoryQueryMapper",
    "CategoryResponseMapper",
    "CategoryStatsMapper",
    "map_categories_monthly_total_price",
    "map_categories_monthly_total_prices",
    "map_categories_yearly_total_price",
    "map_categories_yearly_total_prices",
    "map_category_month_price",
    "map_category_month_prices",
    "map_category_response",
    "map_category_response_delete_at",
    "map_category_year_price",
    "map_category_year_prices",
    "map_pagination_meta",
    "new_category_response_mapper",
    "to_api_response_category",
    "to_api_response_category_all",
    "to_api_response_category_delete",
    "to_api_response_category_delete_at",
    "to_api_response_category_month_price",
    "to_api_response_category_monthly_total_price",
    "to_api_response_category_year_price",
    "to_api_response_category_yearly_total_price",
    "to_api_response_pagination_category",
    "to_api_response_pagination_category_delete_at",
    "to_api_responses_category",
    "to_category_response",
    "to_category_response_delete_at",
]
