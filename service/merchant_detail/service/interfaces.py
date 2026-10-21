"""merchant_detail service"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant_detail import (
    CreateMerchantDetailRow,
    CreateMerchantSocialMediaLinkRow,
    GetMerchantDetailRow,
    GetMerchantDetailsActiveRow,
    GetMerchantDetailsRow,
    GetMerchantDetailsTrashedRow,
    MerchantDetail,
    UpdateMerchantDetailRow,
    UpdateMerchantSocialMediaLinkRow,
)
from shared.domain.requests.merchant_detail import (
    CreateMerchantDetailRequest,
    CreateMerchantSocialRequest,
    UpdateMerchantDetailRequest,
    UpdateMerchantSocialRequest,
)


class MerchantDetailQueryService(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantDetailsRow], int]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantDetailsActiveRow], int]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantDetailsTrashedRow], int]: ...

    async def find_by_id(self, merchant_detail_id: int) -> GetMerchantDetailRow: ...


class MerchantDetailCommandService(Protocol):
    async def create(
        self, request: CreateMerchantDetailRequest
    ) -> CreateMerchantDetailRow: ...

    async def update(
        self, request: UpdateMerchantDetailRequest
    ) -> UpdateMerchantDetailRow: ...

    async def trash(self, merchant_detail_id: int) -> MerchantDetail: ...

    async def restore(self, merchant_detail_id: int) -> MerchantDetail: ...

    async def delete_permanent(self, merchant_detail_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


class MerchantSocialLinkCommandService(Protocol):
    async def create(
        self, request: CreateMerchantSocialRequest
    ) -> CreateMerchantSocialMediaLinkRow: ...

    async def update(
        self, request: UpdateMerchantSocialRequest
    ) -> UpdateMerchantSocialMediaLinkRow: ...

    async def trash(self, social_id: int) -> bool: ...

    async def restore(self, social_id: int) -> bool: ...

    async def delete_permanent(self, social_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


__all__ = [
    "MerchantDetailCommandService",
    "MerchantDetailQueryService",
    "MerchantSocialLinkCommandService",
]
