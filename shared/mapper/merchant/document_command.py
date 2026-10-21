"""Merchant document command response mapping. `Create`/`Update`/`UpdateStatus`/`Trash`/`Restore` all return the plain `ApiResponseMerchantDocument` (reused from the query side), so only the command-only envelopes live here. `DeletePermanent` maps the `ApiResponseMerchantDocumentDelete` proto onto the status/message-only `ApiResponseMerchantDocumentDelete` REST DTO — i.e. an empty-data envelope."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import ApiResponse


def to_api_response_merchant_document_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_merchant_document_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


__all__ = [
    "to_api_response_merchant_document_all",
    "to_api_response_merchant_document_delete",
]
