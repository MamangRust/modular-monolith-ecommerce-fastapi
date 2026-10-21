"""Merchant document query response mapping."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant import (
    MerchantDocumentResponse,
    MerchantDocumentResponseDeleteAt,
)
from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
)
from shared.mapper.merchant.mapper import (
    map_merchant_document_response,
    map_merchant_document_response_delete_at,
    map_pagination_meta,
)


def to_api_response_merchant_document(
    pb: Any,
) -> ApiResponse[MerchantDocumentResponse]:
    return ApiResponse[MerchantDocumentResponse](
        status=pb.status,
        message=pb.message,
        data=map_merchant_document_response(pb.data),
    )


def to_api_responses_merchant_document(
    pb: Any,
) -> ApiResponse[list[MerchantDocumentResponse]]:
    return ApiResponse[list[MerchantDocumentResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_document_response(item) for item in pb.data],
    )


def to_api_response_pagination_merchant_document(
    pb: Any,
) -> APIResponsePagination[list[MerchantDocumentResponse]]:
    return APIResponsePagination[list[MerchantDocumentResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_document_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_merchant_document_delete_at(
    pb: Any,
) -> APIResponsePagination[list[MerchantDocumentResponseDeleteAt]]:
    return APIResponsePagination[list[MerchantDocumentResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_merchant_document_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "to_api_response_merchant_document",
    "to_api_response_pagination_merchant_document",
    "to_api_response_pagination_merchant_document_delete_at",
    "to_api_responses_merchant_document",
]
