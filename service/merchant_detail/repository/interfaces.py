"""merchant_detail repository `MerchantQueryRepository` is the cross-domain adapter port (backed by `pkg.adapter.merchant.MerchantQueryAdapter`, which calls the merchant service over gRPC). The other three repositories are SQL-backed."""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant import GetMerchantByIDRow
from pkg.database.schema.merchant_detail import (
    CreateMerchantDetailRow,
    CreateMerchantSocialMediaLinkRow,
    GetMerchantDetailRow,
    GetMerchantDetailsActiveRow,
    GetMerchantDetailsRow,
    GetMerchantDetailsTrashedRow,
    GetMerchantDetailTrashedRow,
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


class MerchantQueryRepository(Protocol):
    async def find_by_id(self, merchant_id: int) -> GetMerchantByIDRow: ...


class MerchantDetailQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantDetailsRow]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantDetailsActiveRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantDetailsTrashedRow]: ...

    async def find_by_id(self, merchant_detail_id: int) -> GetMerchantDetailRow: ...

    async def find_by_id_trashed(
        self, merchant_detail_id: int
    ) -> GetMerchantDetailTrashedRow: ...


class MerchantDetailCommandRepository(Protocol):
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


class MerchantSocialLinkCommandRepository(Protocol):
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
    "MerchantDetailCommandRepository",
    "MerchantDetailQueryRepository",
    "MerchantQueryRepository",
    "MerchantSocialLinkCommandRepository",
]
