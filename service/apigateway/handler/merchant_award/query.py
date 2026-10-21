"""Merchant award query REST routes.

Static paths (`/active`, `/trashed`) are registered before
`/{merchant_award_id}` because Starlette matches routes in registration order
(unlike chi, which prioritises static segments). Without this ordering `/active`
would be captured as merchant_award_id="active"."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.merchant_award.handler import MerchantAwardHandler
from shared.domain.response.merchant_award import (
    MerchantAwardResponse,
    MerchantAwardResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination

router = APIRouter(
    prefix="/api/merchant-award-query", tags=["merchant-award-query"]
)


def get_merchant_award_handler(request: Request) -> MerchantAwardHandler:
    return MerchantAwardHandler(request.app.state.connections)


@router.get("")
async def find_all_merchant_award(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantAwardResponse]]:
    return await get_merchant_award_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_merchant_award(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantAwardResponseDeleteAt]]:
    return await get_merchant_award_handler(request).find_by_active(
        page, page_size, search
    )


@router.get("/trashed")
async def find_trashed_merchant_award(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantAwardResponseDeleteAt]]:
    return await get_merchant_award_handler(request).find_by_trashed(
        page, page_size, search
    )


@router.get("/{merchant_award_id}")
async def find_merchant_award_by_id(
    request: Request,
    merchant_award_id: int,
) -> ApiResponse[MerchantAwardResponse]:
    return await get_merchant_award_handler(request).find_by_id(merchant_award_id)


__all__ = ["router"]
