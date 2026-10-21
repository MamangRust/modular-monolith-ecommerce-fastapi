"""Merchant social link command REST routes. Only the command surface exists (create/update); registers no query routes because the query RPC does not exist. `Create` returns 200 (`c.JSON(http.StatusOK,...)`), NOT 201 like merchant detail create."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.merchant_social_link.handler import (
    MerchantSocialLinkHandler,
)
from shared.domain.requests.merchant_detail import (
    CreateMerchantSocialRequest,
    UpdateMerchantSocialRequest,
)
from shared.domain.response.merchant_detail import MerchantSocialLinkResponse
from shared.domain.response.responses import ApiResponse

router = APIRouter(prefix="/api/merchant-social-link", tags=["merchant-social-link"])


def get_merchant_social_link_handler(request: Request) -> MerchantSocialLinkHandler:
    return MerchantSocialLinkHandler(request.app.state.connections)


@router.post("/create")
async def create_merchant_social_link(
    request: Request,
    body: CreateMerchantSocialRequest,
) -> ApiResponse[MerchantSocialLinkResponse]:
    return await get_merchant_social_link_handler(request).create(
        body.merchant_detail_id,
        body.platform,
        body.url,
    )


@router.post("/update/{social_id}")
async def update_merchant_social_link(
    request: Request,
    social_id: int,
    body: UpdateMerchantSocialRequest,
) -> ApiResponse[MerchantSocialLinkResponse]:
    return await get_merchant_social_link_handler(request).update(
        social_id,
        body.merchant_detail_id,
        body.platform,
        body.url,
    )


__all__ = ["router"]
