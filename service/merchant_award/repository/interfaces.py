"""merchant_award repository `MerchantQueryRepository` is the cross-domain adapter port (backed by `pkg.adapter.merchant.MerchantQueryAdapter`). The other two repositories are SQL-backed. Note: the merchant_award service never consumes `MerchantQueryRepository` (no service path validates the parent merchant — unlike merchant_detail). It is only to keep the repository composition faithful (dead code in both implementations)."""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant import GetMerchantByIDRow
from pkg.database.schema.merchant_award import (
    CreateMerchantCertificationOrAwardRow,
    GetMerchantCertificationOrAwardRow,
    GetMerchantCertificationsAndAwardsActiveRow,
    GetMerchantCertificationsAndAwardsRow,
    GetMerchantCertificationsAndAwardsTrashedRow,
    MerchantCertificationsAndAward,
    UpdateMerchantCertificationOrAwardRow,
)
from shared.domain.requests.merchant_award import (
    CreateMerchantCertificationOrAwardRequest,
    UpdateMerchantCertificationOrAwardRequest,
)


class MerchantQueryRepository(Protocol):
    async def find_by_id(self, merchant_id: int) -> GetMerchantByIDRow: ...


class MerchantAwardQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantCertificationsAndAwardsRow]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantCertificationsAndAwardsActiveRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantCertificationsAndAwardsTrashedRow]: ...

    async def find_by_id(
        self, merchant_certification_id: int
    ) -> GetMerchantCertificationOrAwardRow: ...


class MerchantAwardCommandRepository(Protocol):
    async def create(
        self, request: CreateMerchantCertificationOrAwardRequest
    ) -> CreateMerchantCertificationOrAwardRow: ...

    async def update(
        self, request: UpdateMerchantCertificationOrAwardRequest
    ) -> UpdateMerchantCertificationOrAwardRow: ...

    async def trash(
        self, merchant_certification_id: int
    ) -> MerchantCertificationsAndAward: ...

    async def restore(
        self, merchant_certification_id: int
    ) -> MerchantCertificationsAndAward: ...

    async def delete_permanent(self, merchant_certification_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


__all__ = [
    "MerchantAwardCommandRepository",
    "MerchantAwardQueryRepository",
    "MerchantQueryRepository",
]
