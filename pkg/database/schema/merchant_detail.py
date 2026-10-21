"""Row types for the merchant_details + merchant_social_media_links tables. `display_name`/`cover_image_url`/`logo_url`/`short_description`/`website_url` are nullable in (`*string`), modelled as `str | None`. `social_media_links` is a `json_agg(json_build_object(...)` column. scans it as raw `[]byte`; asyncpg decodes it to a Python list. It is modelled as `Any` and — matching the handler mapping, which never reads it — is *not* projected onto the proto. See the. Timestamps surface as `datetime.datetime` and are formatted `%Y-%m-%d %H:%M:%S.mmm` (`2006-01-02 15:04:05.000`, a new format for this domain — see the)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class MerchantDetail:

    merchant_detail_id: int
    merchant_id: int
    display_name: str | None
    cover_image_url: str | None
    logo_url: str | None
    short_description: str | None
    website_url: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> MerchantDetail:
        return cls(
            merchant_detail_id=row["merchant_detail_id"],
            merchant_id=row["merchant_id"],
            display_name=row.get("display_name"),
            cover_image_url=row.get("cover_image_url"),
            logo_url=row.get("logo_url"),
            short_description=row.get("short_description"),
            website_url=row.get("website_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateMerchantDetailRow:
    """`Create`/`Update` projection — base columns, no `deleted_at`."""

    merchant_detail_id: int
    merchant_id: int
    display_name: str | None
    cover_image_url: str | None
    logo_url: str | None
    short_description: str | None
    website_url: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateMerchantDetailRow:
        return cls(
            merchant_detail_id=row["merchant_detail_id"],
            merchant_id=row["merchant_id"],
            display_name=row.get("display_name"),
            cover_image_url=row.get("cover_image_url"),
            logo_url=row.get("logo_url"),
            short_description=row.get("short_description"),
            website_url=row.get("website_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateMerchantDetailRow = CreateMerchantDetailRow


@dataclass
class GetMerchantDetailRow:
    """Single `GetMerchantDetail` projection: base + `merchant_name` + links. `GetMerchantDetail` has no window count, so unlike the list rows there is no `total_count` here."""

    merchant_detail_id: int
    merchant_id: int
    display_name: str | None
    cover_image_url: str | None
    logo_url: str | None
    short_description: str | None
    website_url: str | None
    created_at: datetime
    updated_at: datetime
    merchant_name: str
    social_media_links: Any

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantDetailRow:
        return cls(
            merchant_detail_id=row["merchant_detail_id"],
            merchant_id=row["merchant_id"],
            display_name=row.get("display_name"),
            cover_image_url=row.get("cover_image_url"),
            logo_url=row.get("logo_url"),
            short_description=row.get("short_description"),
            website_url=row.get("website_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            merchant_name=row["merchant_name"],
            social_media_links=row.get("social_media_links"),
        )


@dataclass
class GetMerchantDetailTrashedRow:
    """`GetMerchantDetailTrashed` projection — base columns only."""

    merchant_detail_id: int
    merchant_id: int
    display_name: str | None
    cover_image_url: str | None
    logo_url: str | None
    short_description: str | None
    website_url: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantDetailTrashedRow:
        return cls(
            merchant_detail_id=row["merchant_detail_id"],
            merchant_id=row["merchant_id"],
            display_name=row.get("display_name"),
            cover_image_url=row.get("cover_image_url"),
            logo_url=row.get("logo_url"),
            short_description=row.get("short_description"),
            website_url=row.get("website_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class GetMerchantDetailsRow:
    """`FindAll` projection with a window total count (active-only)."""

    merchant_detail_id: int
    merchant_id: int
    display_name: str | None
    cover_image_url: str | None
    logo_url: str | None
    short_description: str | None
    website_url: str | None
    created_at: datetime
    updated_at: datetime
    merchant_name: str
    total_count: int
    social_media_links: Any

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantDetailsRow:
        return cls(
            merchant_detail_id=row["merchant_detail_id"],
            merchant_id=row["merchant_id"],
            display_name=row.get("display_name"),
            cover_image_url=row.get("cover_image_url"),
            logo_url=row.get("logo_url"),
            short_description=row.get("short_description"),
            website_url=row.get("website_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            merchant_name=row["merchant_name"],
            total_count=int(row["total_count"]),
            social_media_links=row.get("social_media_links"),
        )


@dataclass
class GetMerchantDetailsActiveRow:
    """`FindActive`/`FindTrashed` projection: carries `deleted_at` + total."""

    merchant_detail_id: int
    merchant_id: int
    display_name: str | None
    cover_image_url: str | None
    logo_url: str | None
    short_description: str | None
    website_url: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    merchant_name: str
    total_count: int
    social_media_links: Any

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantDetailsActiveRow:
        return cls(
            merchant_detail_id=row["merchant_detail_id"],
            merchant_id=row["merchant_id"],
            display_name=row.get("display_name"),
            cover_image_url=row.get("cover_image_url"),
            logo_url=row.get("logo_url"),
            short_description=row.get("short_description"),
            website_url=row.get("website_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            merchant_name=row["merchant_name"],
            total_count=int(row["total_count"]),
            social_media_links=row.get("social_media_links"),
        )


GetMerchantDetailsTrashedRow = GetMerchantDetailsActiveRow


@dataclass
class MerchantSocialMediaLink:

    merchant_social_id: int
    merchant_detail_id: int
    platform: str
    url: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> MerchantSocialMediaLink:
        return cls(
            merchant_social_id=row["merchant_social_id"],
            merchant_detail_id=row["merchant_detail_id"],
            platform=row["platform"],
            url=row["url"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateMerchantSocialMediaLinkRow:
    """`Create`/`Update` projection — no `deleted_at`."""

    merchant_social_id: int
    merchant_detail_id: int
    platform: str
    url: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateMerchantSocialMediaLinkRow:
        return cls(
            merchant_social_id=row["merchant_social_id"],
            merchant_detail_id=row["merchant_detail_id"],
            platform=row["platform"],
            url=row["url"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateMerchantSocialMediaLinkRow = CreateMerchantSocialMediaLinkRow


__all__ = [
    "CreateMerchantDetailRow",
    "CreateMerchantSocialMediaLinkRow",
    "GetMerchantDetailRow",
    "GetMerchantDetailTrashedRow",
    "GetMerchantDetailsActiveRow",
    "GetMerchantDetailsRow",
    "GetMerchantDetailsTrashedRow",
    "MerchantDetail",
    "MerchantSocialMediaLink",
    "UpdateMerchantDetailRow",
    "UpdateMerchantSocialMediaLinkRow",
]
