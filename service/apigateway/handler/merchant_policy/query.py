"""Merchant policy query REST routes.

Static paths (`/active`, `/trashed`) are registered before `/{merchant_policy_id}`
because Starlette matches routes in registration order (unlike chi, which
prioritises static segments). Without this ordering `/active` would be captured
as merchant_policy_id="active"."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.merchant_policy.handler import MerchantPolicyHandler
from shared.domain.response.merchant_policy import (
    MerchantPoliciesResponse,
    MerchantPoliciesResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination

router = APIRouter(prefix="/api/merchant-policy-query", tags=["merchant-policy-query"])


def get_merchant_policy_handler(request: Request) -> MerchantPolicyHandler:
    return MerchantPolicyHandler(request.app.state.connections)


@router.get("")
async def find_all_merchant_policy(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantPoliciesResponse]]:
    return await get_merchant_policy_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_merchant_policy(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantPoliciesResponseDeleteAt]]:
    return await get_merchant_policy_handler(request).find_by_active(
        page, page_size, search
    )


@router.get("/trashed")
async def find_trashed_merchant_policy(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[MerchantPoliciesResponseDeleteAt]]:
    return await get_merchant_policy_handler(request).find_by_trashed(
        page, page_size, search
    )


@router.get("/{merchant_policy_id}")
async def find_merchant_policy_by_id(
    request: Request,
    merchant_policy_id: int,
) -> ApiResponse[MerchantPoliciesResponse]:
    return await get_merchant_policy_handler(request).find_by_id(merchant_policy_id)


__all__ = ["router"]
