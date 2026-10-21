"""Merchant document command REST routes. `Create`/`Update` are multipart form endpoints; `UpdateStatus` is a JSON body endpoint. Static paths (`/restore/all`, `/permanent/all`) are registered before the `{document_id}` variants because Starlette matches in registration order. The form fields are declared optional and validated inside the handler so the error messages match exactly ("Invalid merchant ID", "Document type is required", "Document file is required") instead of FastAPI's generic 422."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, Request, UploadFile

from service.apigateway.handler.merchant_document.handler import (
    MerchantDocumentHandler,
)
from shared.domain.requests.merchant import UpdateMerchantDocumentStatusRequest
from shared.domain.response.merchant import (
    MerchantDocumentResponse,
    MerchantDocumentResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse

router = APIRouter(
    prefix="/api/merchant-document-command", tags=["merchant-document-command"]
)


def get_merchant_document_handler(request: Request) -> MerchantDocumentHandler:
    return MerchantDocumentHandler(
        request.app.state.connections, request.app.state.upload_image
    )


@router.post("/create")
async def create_merchant_document(
    request: Request,
    merchant_id: str = Form(""),
    document_type: str = Form(""),
    document_url: UploadFile | None = File(None),
) -> ApiResponse[MerchantDocumentResponse]:
    return await get_merchant_document_handler(request).create(
        merchant_id, document_type, document_url
    )


@router.post("/update-status/{document_id}")
async def update_status_merchant_document(
    request: Request,
    document_id: int,
    body: UpdateMerchantDocumentStatusRequest,
) -> ApiResponse[MerchantDocumentResponse]:
    return await get_merchant_document_handler(request).update_status(
        document_id, body.merchant_id, body.status, body.note
    )


# Static paths first — `/restore/all` and `/permanent/all` must not be captured
# as document_id="all" by the `/{document_id}` variants below.
@router.post("/restore/all")
async def restore_all_merchant_document(request: Request) -> ApiResponse[None]:
    return await get_merchant_document_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_merchant_document_permanent(
    request: Request,
) -> ApiResponse[None]:
    return await get_merchant_document_handler(request).delete_all_permanent()


@router.post("/update/{document_id}")
async def update_merchant_document(
    request: Request,
    document_id: int,
    merchant_id: str = Form(""),
    document_type: str = Form(""),
    document_url: UploadFile | None = File(None),
    document_url_old: str = Form(""),
    status: str = Form(""),
    note: str = Form(""),
) -> ApiResponse[MerchantDocumentResponse]:
    return await get_merchant_document_handler(request).update(
        document_id,
        merchant_id,
        document_type,
        document_url,
        document_url_old,
        status,
        note,
    )


@router.post("/trashed/{document_id}")
async def trash_merchant_document(
    request: Request,
    document_id: int,
) -> ApiResponse[MerchantDocumentResponse]:
    return await get_merchant_document_handler(request).trash(document_id)


@router.post("/restore/{document_id}")
async def restore_merchant_document(
    request: Request,
    document_id: int,
) -> ApiResponse[MerchantDocumentResponse]:
    return await get_merchant_document_handler(request).restore(document_id)


@router.delete("/permanent/{document_id}")
async def delete_merchant_document_permanent(
    request: Request,
    document_id: int,
) -> ApiResponse[MerchantDocumentResponseDeleteAt]:
    return await get_merchant_document_handler(request).delete_permanent(document_id)


__all__ = ["router"]
