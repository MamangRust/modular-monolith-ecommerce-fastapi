"""product command response mapping. `Create`/`Update` reuse the query-side `to_api_response_product` (identical shape). The `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` envelopes carry no data (`ApiResponse[None]`), matching `ApiResponseProductDelete`/`All`."""

from __future__ import annotations

from typing import Any

from shared.domain.response.product import ProductResponseDeleteAt
from shared.domain.response.responses import ApiResponse
from shared.mapper.product.mapper import map_product_response_delete_at


def to_api_response_product_delete_at(
    pb: Any,
) -> ApiResponse[ProductResponseDeleteAt]:
    return ApiResponse[ProductResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_product_response_delete_at(pb.data),
    )


def to_api_response_product_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](
        status=pb.status,
        message=pb.message,
        data=None,
    )


def to_api_response_product_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](
        status=pb.status,
        message=pb.message,
        data=None,
    )


__all__ = [
    "to_api_response_product_all",
    "to_api_response_product_delete",
    "to_api_response_product_delete_at",
]
