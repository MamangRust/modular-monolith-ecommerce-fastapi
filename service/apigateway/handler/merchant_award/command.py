"""Merchant award command REST routes. Static paths (`/create`, `/restore/all`, `/permanent/all`) are registered before the `{id}` variants because Starlette matches in registration order. `Create` returns 200 (uses `http.StatusOK` here, unlike merchant/merchant_detail which return 201). Every path-id route guards `id <= 0` with 400 `Invalid ID`. `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` return the merchant envelope (`ApiResponse[None]`),."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.merchant_award.handler import MerchantAwardHandler
from shared.domain.requests.merchant_award import (
    CreateMerchantCertificationOrAwardRequest,
    UpdateMerchantCertificationOrAwardRequest,
)
from shared.domain.response.merchant_award import (
    MerchantAwardResponse,
    MerchantAwardResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse

router = APIRouter(
    prefix="/api/merchant-award-command", tags=["merchant-award-command"]
)


def get_merchant_award_handler(request: Request) -> MerchantAwardHandler:
    return MerchantAwardHandler(request.app.state.connections)


@router.post("/create")
async def create_merchant_award(
    request: Request,
    body: CreateMerchantCertificationOrAwardRequest,
) -> ApiResponse[MerchantAwardResponse]:
    return await get_merchant_award_handler(request).create(
        body.merchant_id,
        body.title,
        body.description,
        body.issued_by,
        body.issue_date,
        body.expiry_date,
        body.certificate_url,
    )


# Static paths first — `/restore/all` and `/permanent/all` must not be captured
# as an id by the `/{...}` variants below.
@router.post("/restore/all")
async def restore_all_merchant_award(request: Request) -> ApiResponse[None]:
    return await get_merchant_award_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_merchant_award_permanent(request: Request) -> ApiResponse[None]:
    return await get_merchant_award_handler(request).delete_all_permanent()


@router.post("/update/{merchant_award_id}")
async def update_merchant_award(
    request: Request,
    merchant_award_id: int,
    body: UpdateMerchantCertificationOrAwardRequest,
) -> ApiResponse[MerchantAwardResponse]:
    return await get_merchant_award_handler(request).update(
        merchant_award_id,
        body.title,
        body.description,
        body.issued_by,
        body.issue_date,
        body.expiry_date,
        body.certificate_url,
    )


@router.post("/trashed/{merchant_award_id}")
async def trash_merchant_award(
    request: Request,
    merchant_award_id: int,
) -> ApiResponse[MerchantAwardResponseDeleteAt]:
    return await get_merchant_award_handler(request).trash(merchant_award_id)


@router.post("/restore/{merchant_award_id}")
async def restore_merchant_award(
    request: Request,
    merchant_award_id: int,
) -> ApiResponse[MerchantAwardResponseDeleteAt]:
    return await get_merchant_award_handler(request).restore(merchant_award_id)


@router.delete("/permanent/{merchant_award_id}")
async def delete_merchant_award_permanent(
    request: Request,
    merchant_award_id: int,
) -> ApiResponse[None]:
    return await get_merchant_award_handler(request).delete_permanent(
        merchant_award_id
    )


__all__ = ["router"]
