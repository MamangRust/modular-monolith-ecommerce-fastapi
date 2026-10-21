"""product REST mappers."""

from __future__ import annotations

from shared.mapper.product.command import (
    to_api_response_product_all,
    to_api_response_product_delete,
    to_api_response_product_delete_at,
)
from shared.mapper.product.mapper import (
    map_pagination_meta,
    map_product_response,
    map_product_response_delete_at,
)
from shared.mapper.product.query import (
    to_api_response_pagination_product,
    to_api_response_pagination_product_delete_at,
    to_api_response_product,
    to_api_responses_products,
)

__all__ = [
    "map_pagination_meta",
    "map_product_response",
    "map_product_response_delete_at",
    "to_api_response_pagination_product",
    "to_api_response_pagination_product_delete_at",
    "to_api_response_product",
    "to_api_response_product_all",
    "to_api_response_product_delete",
    "to_api_response_product_delete_at",
    "to_api_responses_products",
]
