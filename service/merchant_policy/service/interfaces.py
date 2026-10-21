"""merchant_policy service"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant_policy import (
    CreateMerchantPolicyRow,
    GetMerchantPoliciesActiveRow,
    GetMerchantPoliciesRow,
    GetMerchantPoliciesTrashedRow,
    GetMerchantPolicyRow,
    MerchantPolicy,
    UpdateMerchantPolicyRow,
)
from shared.domain.requests.merchant_policy import (
    CreateMerchantPolicyRequest,
    UpdateMerchantPolicyRequest,
)


class MerchantPolicyQueryService(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantPoliciesRow], int]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantPoliciesActiveRow], int]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantPoliciesTrashedRow], int]: ...

    async def find_by_id(self, merchant_policy_id: int) -> GetMerchantPolicyRow: ...


class MerchantPolicyCommandService(Protocol):
    async def create(
        self, request: CreateMerchantPolicyRequest
    ) -> CreateMerchantPolicyRow: ...

    async def update(
        self, request: UpdateMerchantPolicyRequest
    ) -> UpdateMerchantPolicyRow: ...

    async def trash(self, merchant_policy_id: int) -> MerchantPolicy: ...

    async def restore(self, merchant_policy_id: int) -> MerchantPolicy: ...

    async def delete_permanent(self, merchant_policy_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


__all__ = [
    "MerchantPolicyCommandService",
    "MerchantPolicyQueryService",
]
