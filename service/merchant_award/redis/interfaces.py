"""merchant_award cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant_award import (
    GetMerchantCertificationOrAwardRow,
    GetMerchantCertificationsAndAwardsActiveRow,
    GetMerchantCertificationsAndAwardsRow,
    GetMerchantCertificationsAndAwardsTrashedRow,
)


class MerchantAwardQueryCache(Protocol):
    async def get_merchant_awards(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantCertificationsAndAwardsRow], int] | None: ...

    async def set_merchant_awards(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantCertificationsAndAwardsRow],
        total: int,
    ) -> None: ...

    async def get_merchant_awards_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantCertificationsAndAwardsActiveRow], int] | None: ...

    async def set_merchant_awards_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantCertificationsAndAwardsActiveRow],
        total: int,
    ) -> None: ...

    async def get_merchant_awards_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantCertificationsAndAwardsTrashedRow], int] | None: ...

    async def set_merchant_awards_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantCertificationsAndAwardsTrashedRow],
        total: int,
    ) -> None: ...

    async def get_merchant_award(
        self, merchant_certification_id: int
    ) -> GetMerchantCertificationOrAwardRow | None: ...

    async def set_merchant_award(
        self, row: GetMerchantCertificationOrAwardRow
    ) -> None: ...


class MerchantAwardCommandCache(Protocol):
    async def delete_cached_merchant_award(
        self, merchant_certification_id: int
    ) -> int: ...


__all__ = [
    "MerchantAwardCommandCache",
    "MerchantAwardQueryCache",
]
