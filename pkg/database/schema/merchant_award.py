"""Row types for the merchant_certifications_and_awards table. `description`/`issued_by`/`certificate_url` are nullable in (`*string`), modelled as `str | None`. `merchant_name` is present on the list rows and in the proto/REST response but the handler mapping never reads it, so it is always `""` on the wire."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


@dataclass
class MerchantCertificationsAndAward:

    merchant_certification_id: int
    merchant_id: int
    title: str
    description: str | None
    issued_by: str | None
    issue_date: date | None
    expiry_date: date | None
    certificate_url: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> MerchantCertificationsAndAward:
        return cls(
            merchant_certification_id=row["merchant_certification_id"],
            merchant_id=row["merchant_id"],
            title=row["title"],
            description=row.get("description"),
            issued_by=row.get("issued_by"),
            issue_date=row.get("issue_date"),
            expiry_date=row.get("expiry_date"),
            certificate_url=row.get("certificate_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateMerchantCertificationOrAwardRow:
    """`Create`/`Update` projection — base columns, no `deleted_at`."""

    merchant_certification_id: int
    merchant_id: int
    title: str
    description: str | None
    issued_by: str | None
    issue_date: date | None
    expiry_date: date | None
    certificate_url: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateMerchantCertificationOrAwardRow:
        return cls(
            merchant_certification_id=row["merchant_certification_id"],
            merchant_id=row["merchant_id"],
            title=row["title"],
            description=row.get("description"),
            issued_by=row.get("issued_by"),
            issue_date=row.get("issue_date"),
            expiry_date=row.get("expiry_date"),
            certificate_url=row.get("certificate_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateMerchantCertificationOrAwardRow = CreateMerchantCertificationOrAwardRow


@dataclass
class GetMerchantCertificationOrAwardRow:
    """Single `GetMerchantCertificationOrAward` projection — base only."""

    merchant_certification_id: int
    merchant_id: int
    title: str
    description: str | None
    issued_by: str | None
    issue_date: date | None
    expiry_date: date | None
    certificate_url: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantCertificationOrAwardRow:
        return cls(
            merchant_certification_id=row["merchant_certification_id"],
            merchant_id=row["merchant_id"],
            title=row["title"],
            description=row.get("description"),
            issued_by=row.get("issued_by"),
            issue_date=row.get("issue_date"),
            expiry_date=row.get("expiry_date"),
            certificate_url=row.get("certificate_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class GetMerchantCertificationsAndAwardsRow:
    """`FindAll` projection with a window total count (no `deleted_at`)."""

    merchant_certification_id: int
    merchant_id: int
    title: str
    description: str | None
    issued_by: str | None
    issue_date: date | None
    expiry_date: date | None
    certificate_url: str | None
    created_at: datetime
    updated_at: datetime
    merchant_name: str
    total_count: int

    @classmethod
    def from_row(
        cls, row: Mapping[str, Any]
    ) -> GetMerchantCertificationsAndAwardsRow:
        return cls(
            merchant_certification_id=row["merchant_certification_id"],
            merchant_id=row["merchant_id"],
            title=row["title"],
            description=row.get("description"),
            issued_by=row.get("issued_by"),
            issue_date=row.get("issue_date"),
            expiry_date=row.get("expiry_date"),
            certificate_url=row.get("certificate_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            merchant_name=row["merchant_name"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetMerchantCertificationsAndAwardsActiveRow:
    """`FindActive`/`FindTrashed` projection: carries `deleted_at` + total."""

    merchant_certification_id: int
    merchant_id: int
    title: str
    description: str | None
    issued_by: str | None
    issue_date: date | None
    expiry_date: date | None
    certificate_url: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    merchant_name: str
    total_count: int

    @classmethod
    def from_row(
        cls, row: Mapping[str, Any]
    ) -> GetMerchantCertificationsAndAwardsActiveRow:
        return cls(
            merchant_certification_id=row["merchant_certification_id"],
            merchant_id=row["merchant_id"],
            title=row["title"],
            description=row.get("description"),
            issued_by=row.get("issued_by"),
            issue_date=row.get("issue_date"),
            expiry_date=row.get("expiry_date"),
            certificate_url=row.get("certificate_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            merchant_name=row["merchant_name"],
            total_count=int(row["total_count"]),
        )


GetMerchantCertificationsAndAwardsTrashedRow = (
    GetMerchantCertificationsAndAwardsActiveRow
)


__all__ = [
    "CreateMerchantCertificationOrAwardRow",
    "GetMerchantCertificationOrAwardRow",
    "GetMerchantCertificationsAndAwardsActiveRow",
    "GetMerchantCertificationsAndAwardsRow",
    "GetMerchantCertificationsAndAwardsTrashedRow",
    "MerchantCertificationsAndAward",
    "UpdateMerchantCertificationOrAwardRow",
]
