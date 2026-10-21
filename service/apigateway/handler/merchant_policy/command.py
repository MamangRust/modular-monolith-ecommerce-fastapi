"""Merchant policy command REST routes. Static paths (`/create`, `/restore/all`, `/permanent/all`) are registered before the `{id}` variants because Starlette matches in registration order. `Create` returns 200 (uses `http.StatusOK`). Every path-id route guards `id <= 0` with 400 `Invalid ID`. `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` return the merchant envelope (`ApiResponse[None]`),."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.merchant_policy.handler import MerchantPolicyHandler
from shared.domain.requests.merchant_policy import (
    CreateMerchantPolicyRequest,
    UpdateMerchantPolicyRequest,
)
from shared.domain.response.merchant_policy import (
    MerchantPoliciesResponse,
    MerchantPoliciesResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse

router = APIRouter(
    prefix="/api/merchant-policy-command", tags=["merchant-policy-command"]
)


def get_merchant_policy_handler(request: Request) -> MerchantPolicyHandler:
    return MerchantPolicyHandler(request.app.state.connections)


@router.post("/create")
async def create_merchant_policy(
    request: Request,
    body: CreateMerchantPolicyRequest,
) -> ApiResponse[MerchantPoliciesResponse]:
    return await get_merchant_policy_handler(request).create(
        body.merchant_id,
        body.policy_type,
        body.title,
        body.description,
    )


# Static paths first — `/restore/all` and `/permanent/all` must not be captured
# as an id by the `/{...}` variants below.
@router.post("/restore/all")
async def restore_all_merchant_policy(request: Request) -> ApiResponse[None]:
    return await get_merchant_policy_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_merchant_policy_permanent(request: Request) -> ApiResponse[None]:
    return await get_merchant_policy_handler(request).delete_all_permanent()


@router.post("/update/{merchant_policy_id}")
async def update_merchant_policy(
    request: Request,
    merchant_policy_id: int,
    body: UpdateMerchantPolicyRequest,
) -> ApiResponse[MerchantPoliciesResponse]:
    return await get_merchant_policy_handler(request).update(
        merchant_policy_id,
        body.policy_type,
        body.title,
        body.description,
    )


@router.post("/trashed/{merchant_policy_id}")
async def trash_merchant_policy(
    request: Request,
    merchant_policy_id: int,
) -> ApiResponse[MerchantPoliciesResponseDeleteAt]:
    return await get_merchant_policy_handler(request).trash(merchant_policy_id)


@router.post("/restore/{merchant_policy_id}")
async def restore_merchant_policy(
    request: Request,
    merchant_policy_id: int,
) -> ApiResponse[MerchantPoliciesResponseDeleteAt]:
    return await get_merchant_policy_handler(request).restore(merchant_policy_id)


@router.delete("/permanent/{merchant_policy_id}")
async def delete_merchant_policy_permanent(
    request: Request,
    merchant_policy_id: int,
) -> ApiResponse[None]:
    return await get_merchant_policy_handler(request).delete_permanent(
        merchant_policy_id
    )


__all__ = ["router"]
