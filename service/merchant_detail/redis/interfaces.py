"""merchant_detail cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant_detail import (
    GetMerchantDetailRow,
    GetMerchantDetailsActiveRow,
    GetMerchantDetailsRow,
    GetMerchantDetailsTrashedRow,
)


class MerchantDetailQueryCache(Protocol):
    async def get_merchant_details(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantDetailsRow], int] | None: ...

    async def set_merchant_details(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantDetailsRow],
        total: int,
    ) -> None: ...

    async def get_merchant_details_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantDetailsActiveRow], int] | None: ...

    async def set_merchant_details_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantDetailsActiveRow],
        total: int,
    ) -> None: ...

    async def get_merchant_details_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantDetailsTrashedRow], int] | None: ...

    async def set_merchant_details_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantDetailsTrashedRow],
        total: int,
    ) -> None: ...

    async def get_merchant_detail(
        self, merchant_detail_id: int
    ) -> GetMerchantDetailRow | None: ...

    async def set_merchant_detail(self, row: GetMerchantDetailRow) -> None: ...


class MerchantDetailCommandCache(Protocol):
    async def delete_cached_merchant_detail(self, merchant_detail_id: int) -> int: ...


__all__ = [
    "MerchantDetailCommandCache",
    "MerchantDetailQueryCache",
]
