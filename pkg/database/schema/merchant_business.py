"""Row types for the merchant_business_information table. `business_type`/`tax_id`/`website_url` are nullable in (`*string`), modelled as `str | None`; `established_year`/`number_of_employees` are `*int32`, modelled as `int | None`. All timestamps are `pgtype.Timestamp` and are formatted `2006-01-02 15:04:05.000` (no DATE columns here, unlike merchant_award). `merchant_name` is present on the list rows and in the proto/REST response but the handler mapping never reads it, so it is always `""` on the wire."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class MerchantBusinessInformation:

    merchant_business_info_id: int
    merchant_id: int
    business_type: str | None
    tax_id: str | None
    established_year: int | None
    number_of_employees: int | None
    website_url: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> MerchantBusinessInformation:
        return cls(
            merchant_business_info_id=row["merchant_business_info_id"],
            merchant_id=row["merchant_id"],
            business_type=row.get("business_type"),
            tax_id=row.get("tax_id"),
            established_year=row.get("established_year"),
            number_of_employees=row.get("number_of_employees"),
            website_url=row.get("website_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateMerchantBusinessInformationRow:
    """`Create`/`Update` projection — base columns, no `deleted_at`."""

    merchant_business_info_id: int
    merchant_id: int
    business_type: str | None
    tax_id: str | None
    established_year: int | None
    number_of_employees: int | None
    website_url: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateMerchantBusinessInformationRow:
        return cls(
            merchant_business_info_id=row["merchant_business_info_id"],
            merchant_id=row["merchant_id"],
            business_type=row.get("business_type"),
            tax_id=row.get("tax_id"),
            established_year=row.get("established_year"),
            number_of_employees=row.get("number_of_employees"),
            website_url=row.get("website_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateMerchantBusinessInformationRow = CreateMerchantBusinessInformationRow


@dataclass
class GetMerchantBusinessInformationRow:
    """Single `GetMerchantBusinessInformation` projection — base only."""

    merchant_business_info_id: int
    merchant_id: int
    business_type: str | None
    tax_id: str | None
    established_year: int | None
    number_of_employees: int | None
    website_url: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantBusinessInformationRow:
        return cls(
            merchant_business_info_id=row["merchant_business_info_id"],
            merchant_id=row["merchant_id"],
            business_type=row.get("business_type"),
            tax_id=row.get("tax_id"),
            established_year=row.get("established_year"),
            number_of_employees=row.get("number_of_employees"),
            website_url=row.get("website_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class GetMerchantsBusinessInformationRow:
    """`FindAll` projection with a window total count (no `deleted_at`)."""

    merchant_business_info_id: int
    merchant_id: int
    business_type: str | None
    tax_id: str | None
    established_year: int | None
    number_of_employees: int | None
    website_url: str | None
    created_at: datetime
    updated_at: datetime
    merchant_name: str
    total_count: int

    @classmethod
    def from_row(
        cls, row: Mapping[str, Any]
    ) -> GetMerchantsBusinessInformationRow:
        return cls(
            merchant_business_info_id=row["merchant_business_info_id"],
            merchant_id=row["merchant_id"],
            business_type=row.get("business_type"),
            tax_id=row.get("tax_id"),
            established_year=row.get("established_year"),
            number_of_employees=row.get("number_of_employees"),
            website_url=row.get("website_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            merchant_name=row["merchant_name"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetMerchantsBusinessInformationActiveRow:
    """`FindActive`/`FindTrashed` projection: carries `deleted_at` + total."""

    merchant_business_info_id: int
    merchant_id: int
    business_type: str | None
    tax_id: str | None
    established_year: int | None
    number_of_employees: int | None
    website_url: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    merchant_name: str
    total_count: int

    @classmethod
    def from_row(
        cls, row: Mapping[str, Any]
    ) -> GetMerchantsBusinessInformationActiveRow:
        return cls(
            merchant_business_info_id=row["merchant_business_info_id"],
            merchant_id=row["merchant_id"],
            business_type=row.get("business_type"),
            tax_id=row.get("tax_id"),
            established_year=row.get("established_year"),
            number_of_employees=row.get("number_of_employees"),
            website_url=row.get("website_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            merchant_name=row["merchant_name"],
            total_count=int(row["total_count"]),
        )


GetMerchantsBusinessInformationTrashedRow = GetMerchantsBusinessInformationActiveRow


__all__ = [
    "CreateMerchantBusinessInformationRow",
    "GetMerchantBusinessInformationRow",
    "GetMerchantsBusinessInformationActiveRow",
    "GetMerchantsBusinessInformationRow",
    "GetMerchantsBusinessInformationTrashedRow",
    "MerchantBusinessInformation",
    "UpdateMerchantBusinessInformationRow",
]
