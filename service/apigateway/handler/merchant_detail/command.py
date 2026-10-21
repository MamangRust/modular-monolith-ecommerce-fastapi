"""Merchant detail command REST routes. Static paths (`/create`, `/restore/all`, `/permanent/all`) are registered before the `{id}` variants because Starlette matches in registration order. `Create` returns 201, matching. The command id guards use `require_positive_id` (400 `Invalid ID`), the deliberate cross-domain deviation from parse-error-only guard. `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` return the merchant envelope (`ApiResponse[None]`),."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from service.apigateway.handler.merchant_detail.handler import MerchantDetailHandler
from shared.domain.requests.merchant_detail import (
    CreateMerchantDetailRequest,
    UpdateMerchantDetailRequest,
)
from shared.domain.response.merchant_detail import (
    MerchantDetailResponse,
    MerchantDetailResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse

router = APIRouter(
    prefix="/api/merchant-detail-command", tags=["merchant-detail-command"]
)


def get_merchant_detail_handler(request: Request) -> MerchantDetailHandler:
    return MerchantDetailHandler(request.app.state.connections)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_merchant_detail(
    request: Request,
    body: CreateMerchantDetailRequest,
) -> ApiResponse[MerchantDetailResponse]:
    return await get_merchant_detail_handler(request).create(
        body.merchant_id,
        body.display_name,
        body.cover_image_url,
        body.logo_url,
        body.short_description,
        body.website_url,
    )


# Static paths first — `/restore/all` and `/permanent/all` must not be captured
# as an id by the `/{...}` variants below.
@router.post("/restore/all")
async def restore_all_merchant_detail(request: Request) -> ApiResponse[None]:
    return await get_merchant_detail_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_merchant_detail_permanent(request: Request) -> ApiResponse[None]:
    return await get_merchant_detail_handler(request).delete_all_permanent()


@router.post("/update/{merchant_detail_id}")
async def update_merchant_detail(
    request: Request,
    merchant_detail_id: int,
    body: UpdateMerchantDetailRequest,
) -> ApiResponse[MerchantDetailResponse]:
    return await get_merchant_detail_handler(request).update(
        merchant_detail_id,
        body.display_name,
        body.cover_image_url,
        body.logo_url,
        body.short_description,
        body.website_url,
    )


@router.post("/trashed/{merchant_detail_id}")
async def trash_merchant_detail(
    request: Request,
    merchant_detail_id: int,
) -> ApiResponse[MerchantDetailResponseDeleteAt]:
    return await get_merchant_detail_handler(request).trash(merchant_detail_id)


@router.post("/restore/{merchant_detail_id}")
async def restore_merchant_detail(
    request: Request,
    merchant_detail_id: int,
) -> ApiResponse[MerchantDetailResponseDeleteAt]:
    return await get_merchant_detail_handler(request).restore(merchant_detail_id)


@router.delete("/permanent/{merchant_detail_id}")
async def delete_merchant_detail_permanent(
    request: Request,
    merchant_detail_id: int,
) -> ApiResponse[None]:
    return await get_merchant_detail_handler(request).delete_permanent(
        merchant_detail_id
    )


__all__ = ["router"]
