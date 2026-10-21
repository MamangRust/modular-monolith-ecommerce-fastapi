"""merchant_policy repository `MerchantQueryRepository` is the cross-domain adapter port (backed by `pkg.adapter.merchant.MerchantQueryAdapter`). The other two repositories are SQL-backed. Note: the merchant_policy service never consumes `MerchantQueryRepository` (no service path validates the parent merchant — the repository composition just wires it). It is only to keep the composition faithful (dead code in both implementations, like merchant_award/merchant_business)."""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant import GetMerchantByIDRow
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


class MerchantQueryRepository(Protocol):
    async def find_by_id(self, merchant_id: int) -> GetMerchantByIDRow: ...


class MerchantPolicyQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantPoliciesRow]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantPoliciesActiveRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantPoliciesTrashedRow]: ...

    async def find_by_id(self, merchant_policy_id: int) -> GetMerchantPolicyRow: ...


class MerchantPolicyCommandRepository(Protocol):
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
    "MerchantPolicyCommandRepository",
    "MerchantPolicyQueryRepository",
    "MerchantQueryRepository",
]
