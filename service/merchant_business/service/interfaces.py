"""merchant_business service"""

from __future__ import annotations

from typing import Protocol

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


class MerchantBusinessQueryService(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsBusinessInformationRow], int]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsBusinessInformationActiveRow], int]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsBusinessInformationTrashedRow], int]: ...

    async def find_by_id(
        self, merchant_business_info_id: int
    ) -> GetMerchantBusinessInformationRow: ...


class MerchantBusinessCommandService(Protocol):
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
    "MerchantBusinessCommandService",
    "MerchantBusinessQueryService",
]
