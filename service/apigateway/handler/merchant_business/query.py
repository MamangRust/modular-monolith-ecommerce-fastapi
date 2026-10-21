"""Merchant business query REST routes.

Static paths (`/active`, `/trashed`) are registered before
`/{merchant_business_id}` because Starlette matches routes in registration order
(unlike chi, which prioritises static segments). Without this ordering `/active`
would be captured as merchant_business_id="active"."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.merchant_business.handler import (
    MerchantBusinessHandler,
)
from shared.domain.response.merchant_business import (
    MerchantBusinessResponse,
    MerchantBusinessResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination

router = APIRouter(
    prefix="/api/merchant-business-query", tags=["merchant-business-query"]
)


def get_merchant_business_handler(request: Request) -> MerchantBusinessHandler:
    return MerchantBusinessHandler(request.app.state.connections)


@router.get("")
async def find_all_merchant_business(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantBusinessResponse]]:
    return await get_merchant_business_handler(request).find_all(
        page, page_size, search
    )


@router.get("/active")
async def find_active_merchant_business(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantBusinessResponseDeleteAt]]:
    return await get_merchant_business_handler(request).find_by_active(
        page, page_size, search
    )


@router.get("/trashed")
async def find_trashed_merchant_business(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantBusinessResponseDeleteAt]]:
    return await get_merchant_business_handler(request).find_by_trashed(
        page, page_size, search
    )


@router.get("/{merchant_business_id}")
async def find_merchant_business_by_id(
    request: Request,
    merchant_business_id: int,
) -> ApiResponse[MerchantBusinessResponse]:
    return await get_merchant_business_handler(request).find_by_id(
        merchant_business_id
    )


__all__ = ["router"]
