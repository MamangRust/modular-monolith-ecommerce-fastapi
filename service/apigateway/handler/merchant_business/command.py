"""Merchant business command REST routes. Static paths (`/create`, `/restore/all`, `/permanent/all`) are registered before the `{id}` variants because Starlette matches in registration order. `Create` returns 200 (uses `http.StatusOK`). Every path-id route guards `id <= 0` with 400 `Invalid ID`. `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` return the merchant envelope (`ApiResponse[None]`),."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.merchant_business.handler import (
    MerchantBusinessHandler,
)
from shared.domain.requests.merchant_business import (
    CreateMerchantBusinessInformationRequest,
    UpdateMerchantBusinessInformationRequest,
)
from shared.domain.response.merchant_business import (
    MerchantBusinessResponse,
    MerchantBusinessResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse

router = APIRouter(
    prefix="/api/merchant-business-command", tags=["merchant-business-command"]
)


def get_merchant_business_handler(request: Request) -> MerchantBusinessHandler:
    return MerchantBusinessHandler(request.app.state.connections)


@router.post("/create")
async def create_merchant_business(
    request: Request,
    body: CreateMerchantBusinessInformationRequest,
) -> ApiResponse[MerchantBusinessResponse]:
    return await get_merchant_business_handler(request).create(
        body.merchant_id,
        body.business_type,
        body.tax_id,
        body.established_year,
        body.number_of_employees,
        body.website_url,
    )


# Static paths first — `/restore/all` and `/permanent/all` must not be captured
# as an id by the `/{...}` variants below.
@router.post("/restore/all")
async def restore_all_merchant_business(request: Request) -> ApiResponse[None]:
    return await get_merchant_business_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_merchant_business_permanent(request: Request) -> ApiResponse[None]:
    return await get_merchant_business_handler(request).delete_all_permanent()


@router.post("/update/{merchant_business_id}")
async def update_merchant_business(
    request: Request,
    merchant_business_id: int,
    body: UpdateMerchantBusinessInformationRequest,
) -> ApiResponse[MerchantBusinessResponse]:
    return await get_merchant_business_handler(request).update(
        merchant_business_id,
        body.business_type,
        body.tax_id,
        body.established_year,
        body.number_of_employees,
        body.website_url,
    )


@router.post("/trashed/{merchant_business_id}")
async def trash_merchant_business(
    request: Request,
    merchant_business_id: int,
) -> ApiResponse[MerchantBusinessResponseDeleteAt]:
    return await get_merchant_business_handler(request).trash(merchant_business_id)


@router.post("/restore/{merchant_business_id}")
async def restore_merchant_business(
    request: Request,
    merchant_business_id: int,
) -> ApiResponse[MerchantBusinessResponseDeleteAt]:
    return await get_merchant_business_handler(request).restore(merchant_business_id)


@router.delete("/permanent/{merchant_business_id}")
async def delete_merchant_business_permanent(
    request: Request,
    merchant_business_id: int,
) -> ApiResponse[None]:
    return await get_merchant_business_handler(request).delete_permanent(
        merchant_business_id
    )


__all__ = ["router"]
