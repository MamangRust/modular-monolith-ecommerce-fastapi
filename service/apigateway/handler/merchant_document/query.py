"""Merchant document query REST routes.

Static paths (`/active`, `/trashed`) are registered before `/{document_id}`
because Starlette matches routes in registration order."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.merchant_document.handler import (
    MerchantDocumentHandler,
)
from shared.domain.response.merchant import (
    MerchantDocumentResponse,
    MerchantDocumentResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination

router = APIRouter(
    prefix="/api/merchant-document-query", tags=["merchant-document-query"]
)


def get_merchant_document_handler(request: Request) -> MerchantDocumentHandler:
    return MerchantDocumentHandler(
        request.app.state.connections, request.app.state.upload_image
    )


@router.get("")
async def find_all_merchant_document(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantDocumentResponse]]:
    return await get_merchant_document_handler(request).find_all(
        page, page_size, search
    )


@router.get("/active")
async def find_active_merchant_document(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantDocumentResponse]]:
    return await get_merchant_document_handler(request).find_all_active(
        page, page_size, search
    )


@router.get("/trashed")
async def find_trashed_merchant_document(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantDocumentResponseDeleteAt]]:
    return await get_merchant_document_handler(request).find_all_trashed(
        page, page_size, search
    )


@router.get("/{document_id}")
async def find_merchant_document_by_id(
    request: Request,
    document_id: int,
) -> ApiResponse[MerchantDocumentResponse]:
    return await get_merchant_document_handler(request).find_by_id(document_id)


__all__ = ["router"]
