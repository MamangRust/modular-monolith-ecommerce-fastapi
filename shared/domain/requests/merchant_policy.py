"""merchant_policy request DTOs. Validation Matches the expected `validator` tags: - create: `merchant_id` (`required` → non-zero), `policy_type`, `title`, `description` required; - update: same fields plus `merchant_policy_id` (`required`), which the caller supplies (the gRPC handler / gateway attaches it)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateMerchantPolicyRequest(BaseModel):
    merchant_id: int = Field(..., ge=1)
    policy_type: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class UpdateMerchantPolicyRequest(BaseModel):
    merchant_policy_id: int | None = None
    policy_type: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


__all__ = [
    "CreateMerchantPolicyRequest",
    "UpdateMerchantPolicyRequest",
]
