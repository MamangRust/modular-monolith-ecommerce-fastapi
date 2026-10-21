"""merchant_business repository `MerchantQueryRepository` is the cross-domain adapter port (backed by `pkg.adapter.merchant.MerchantQueryAdapter`). The other two repositories are SQL-backed. Note: the merchant_business service never consumes `MerchantQueryRepository` (no service path validates the parent merchant — the repository composition just wires it). It is only to keep the composition faithful (dead code in both implementations, like merchant_award)."""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant import GetMerchantByIDRow
from pkg.database.schema.merchant_business import (
    CreateMerchantBusinessInformationRow,
    GetMerchantBusinessInformationRow,
    GetMerchantsBusinessInformationActiveRow,
    GetMerchantsBusinessInformationRow,
    GetMerchantsBusinessInformationTrashedRow,
    MerchantBusinessInformation,
    UpdateMerchantBusinessInformationRow,
)
from shared.domain.requests.merchant_business import (
    CreateMerchantBusinessInformationRequest,
    UpdateMerchantBusinessInformationRequest,
)


class MerchantQueryRepository(Protocol):
    async def find_by_id(self, merchant_id: int) -> GetMerchantByIDRow: ...


class MerchantBusinessQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsBusinessInformationRow]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsBusinessInformationActiveRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsBusinessInformationTrashedRow]: ...

    async def find_by_id(
        self, merchant_business_info_id: int
    ) -> GetMerchantBusinessInformationRow: ...


class MerchantBusinessCommandRepository(Protocol):
    async def create(
        self, request: CreateMerchantBusinessInformationRequest
    ) -> CreateMerchantBusinessInformationRow: ...

    async def update(
        self, request: UpdateMerchantBusinessInformationRequest
    ) -> UpdateMerchantBusinessInformationRow: ...

    async def trash(
        self, merchant_business_info_id: int
    ) -> MerchantBusinessInformation: ...

    async def restore(
        self, merchant_business_info_id: int
    ) -> MerchantBusinessInformation: ...

    async def delete_permanent(self, merchant_business_info_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


__all__ = [
    "MerchantBusinessCommandRepository",
    "MerchantBusinessQueryRepository",
    "MerchantQueryRepository",
]
