"""merchant_award service"""

from __future__ import annotations

from typing import Protocol

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


class MerchantAwardQueryService(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantCertificationsAndAwardsRow], int]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantCertificationsAndAwardsActiveRow], int]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantCertificationsAndAwardsTrashedRow], int]: ...

    async def find_by_id(
        self, merchant_certification_id: int
    ) -> GetMerchantCertificationOrAwardRow: ...


class MerchantAwardCommandService(Protocol):
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
    "MerchantAwardCommandService",
    "MerchantAwardQueryService",
]
