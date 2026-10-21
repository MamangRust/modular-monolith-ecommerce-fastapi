"""Merchant query REST routes.

Static paths (`/active`, `/trashed`) are registered before `/{merchant_id}`
because Starlette matches routes in registration order (unlike chi, which
prioritises static segments). Without this ordering `/active` would be captured
as merchant_id="active"."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.merchant.handler import MerchantHandler
from shared.domain.response.merchant import (
    MerchantResponse,
    MerchantResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination

router = APIRouter(prefix="/api/merchant-query", tags=["merchant-query"])


def get_merchant_handler(request: Request) -> MerchantHandler:
    return MerchantHandler(request.app.state.connections)


@router.get("")
async def find_all_merchant(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantResponse]]:
    return await get_merchant_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_merchant(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantResponseDeleteAt]]:
    return await get_merchant_handler(request).find_by_active(page, page_size, search)


@router.get("/trashed")
async def find_trashed_merchant(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantResponseDeleteAt]]:
    return await get_merchant_handler(request).find_by_trashed(page, page_size, search)


@router.get("/{merchant_id}")
async def find_merchant_by_id(
    request: Request,
    merchant_id: int,
) -> ApiResponse[MerchantResponse]:
    return await get_merchant_handler(request).find_by_id(merchant_id)


__all__ = ["router"]
