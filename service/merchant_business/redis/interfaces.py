"""merchant_business cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant_business import (
    GetMerchantBusinessInformationRow,
    GetMerchantsBusinessInformationActiveRow,
    GetMerchantsBusinessInformationRow,
    GetMerchantsBusinessInformationTrashedRow,
)


class MerchantBusinessQueryCache(Protocol):
    async def get_merchant_businesses(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsBusinessInformationRow], int] | None: ...

    async def set_merchant_businesses(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsBusinessInformationRow],
        total: int,
    ) -> None: ...

    async def get_merchant_businesses_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsBusinessInformationActiveRow], int] | None: ...

    async def set_merchant_businesses_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsBusinessInformationActiveRow],
        total: int,
    ) -> None: ...

    async def get_merchant_businesses_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsBusinessInformationTrashedRow], int] | None: ...

    async def set_merchant_businesses_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsBusinessInformationTrashedRow],
        total: int,
    ) -> None: ...

    async def get_merchant_business(
        self, merchant_business_info_id: int
    ) -> GetMerchantBusinessInformationRow | None: ...

    async def set_merchant_business(
        self, row: GetMerchantBusinessInformationRow
    ) -> None: ...


class MerchantBusinessCommandCache(Protocol):
    async def delete_cached_merchant_business(
        self, merchant_business_info_id: int
    ) -> int: ...


__all__ = [
    "MerchantBusinessCommandCache",
    "MerchantBusinessQueryCache",
]
