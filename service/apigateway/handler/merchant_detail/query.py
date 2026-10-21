"""Merchant detail query REST routes.

Static paths (`/active`, `/trashed`) are registered before `/{merchant_detail_id}`
because Starlette matches routes in registration order (unlike chi, which
prioritises static segments). Without this ordering `/active` would be captured
as merchant_detail_id="active"."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.merchant_detail.handler import MerchantDetailHandler
from shared.domain.response.merchant_detail import (
    MerchantDetailResponse,
    MerchantDetailResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination

router = APIRouter(
    prefix="/api/merchant-detail-query", tags=["merchant-detail-query"]
)


def get_merchant_detail_handler(request: Request) -> MerchantDetailHandler:
    return MerchantDetailHandler(request.app.state.connections)


@router.get("")
async def find_all_merchant_detail(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantDetailResponse]]:
    return await get_merchant_detail_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_merchant_detail(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantDetailResponseDeleteAt]]:
    return await get_merchant_detail_handler(request).find_by_active(
        page, page_size, search
    )


@router.get("/trashed")
async def find_trashed_merchant_detail(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantDetailResponseDeleteAt]]:
    return await get_merchant_detail_handler(request).find_by_trashed(
        page, page_size, search
    )


@router.get("/{merchant_detail_id}")
async def find_merchant_detail_by_id(
    request: Request,
    merchant_detail_id: int,
) -> ApiResponse[MerchantDetailResponse]:
    return await get_merchant_detail_handler(request).find_by_id(merchant_detail_id)


__all__ = ["router"]
