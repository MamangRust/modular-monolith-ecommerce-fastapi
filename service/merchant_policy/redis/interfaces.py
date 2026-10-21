"""merchant_policy cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant_policy import (
    GetMerchantPoliciesActiveRow,
    GetMerchantPoliciesRow,
    GetMerchantPoliciesTrashedRow,
    GetMerchantPolicyRow,
)


class MerchantPolicyQueryCache(Protocol):
    async def get_merchant_policies(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantPoliciesRow], int] | None: ...

    async def set_merchant_policies(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantPoliciesRow],
        total: int,
    ) -> None: ...

    async def get_merchant_policies_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantPoliciesActiveRow], int] | None: ...

    async def set_merchant_policies_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantPoliciesActiveRow],
        total: int,
    ) -> None: ...

    async def get_merchant_policies_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantPoliciesTrashedRow], int] | None: ...

    async def set_merchant_policies_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantPoliciesTrashedRow],
        total: int,
    ) -> None: ...

    async def get_merchant_policy(
        self, merchant_policy_id: int
    ) -> GetMerchantPolicyRow | None: ...

    async def set_merchant_policy(self, row: GetMerchantPolicyRow) -> None: ...


class MerchantPolicyCommandCache(Protocol):
    async def delete_cached_merchant_policy(self, merchant_policy_id: int) -> int: ...


__all__ = [
    "MerchantPolicyCommandCache",
    "MerchantPolicyQueryCache",
]
