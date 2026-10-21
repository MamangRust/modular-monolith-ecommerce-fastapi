"""Merchant command REST routes. Static paths (`/create`, `/restore/all`, `/permanent/all`) are registered before the `{merchant_id}` variants because Starlette matches in registration order. `Create` returns 201, matching. the gateway exposes no `update-status` route even though the gRPC service has `UpdateStatus`; surface identical."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from service.apigateway.handler.merchant.handler import MerchantHandler
from shared.domain.requests.merchant import (
    CreateMerchantRequest,
    UpdateMerchantRequest,
)
from shared.domain.response.merchant import (
    MerchantResponse,
    MerchantResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse

router = APIRouter(prefix="/api/merchant-command", tags=["merchant-command"])


def get_merchant_handler(request: Request) -> MerchantHandler:
    return MerchantHandler(request.app.state.connections)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_merchant(
    request: Request,
    body: CreateMerchantRequest,
) -> ApiResponse[MerchantResponse]:
    return await get_merchant_handler(request).create(
        getattr(request.state, "user_id", None),
        body.name,
        body.description,
        body.address,
        body.contact_email,
        body.contact_phone,
        body.status,
    )


# Static paths first — `/restore/all` and `/permanent/all` must not be captured
# as merchant_id="all" by the `/{merchant_id}` variants below.
@router.post("/restore/all")
async def restore_all_merchant(request: Request) -> ApiResponse[None]:
    return await get_merchant_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_merchant_permanent(request: Request) -> ApiResponse[None]:
    return await get_merchant_handler(request).delete_all_permanent()


@router.post("/update/{merchant_id}")
async def update_merchant(
    request: Request,
    merchant_id: int,
    body: UpdateMerchantRequest,
) -> ApiResponse[MerchantResponse]:
    return await get_merchant_handler(request).update(
        merchant_id,
        getattr(request.state, "user_id", None),
        body.name,
        body.description,
        body.address,
        body.contact_email,
        body.contact_phone,
        body.status,
    )


@router.post("/trashed/{merchant_id}")
async def trash_merchant(
    request: Request,
    merchant_id: int,
) -> ApiResponse[MerchantResponseDeleteAt]:
    return await get_merchant_handler(request).trash(merchant_id)


@router.post("/restore/{merchant_id}")
async def restore_merchant(
    request: Request,
    merchant_id: int,
) -> ApiResponse[MerchantResponse]:
    return await get_merchant_handler(request).restore(merchant_id)


@router.delete("/permanent/{merchant_id}")
async def delete_merchant_permanent(
    request: Request,
    merchant_id: int,
) -> ApiResponse[None]:
    return await get_merchant_handler(request).delete_permanent(merchant_id)


__all__ = ["router"]
