"""Row types for the banners table. Date/time columns surface as `datetime.date` / `datetime.time`; `is_active` is nullable at the SQL level (models it as `*bool`)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any


@dataclass
class Banner:

    banner_id: int
    name: str
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> Banner:
        return cls(
            banner_id=row["banner_id"],
            name=row["name"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateBannerRow:
    banner_id: int
    name: str
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateBannerRow:
        return cls(
            banner_id=row["banner_id"],
            name=row["name"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class GetBannerRow:
    """`FindByID` projection — active rows only, no `deleted_at`."""

    banner_id: int
    name: str
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetBannerRow:
        return cls(
            banner_id=row["banner_id"],
            name=row["name"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateBannerRow = GetBannerRow


@dataclass
class GetBannersRow:
    """`FindAll` projection with a window total count. Note the SQL carries no `deleted_at` filter, so trashed rows are returned too (see the banner in Planning.md)."""

    banner_id: int
    name: str
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    is_active: bool
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetBannersRow:
        return cls(
            banner_id=row["banner_id"],
            name=row["name"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetBannersActiveRow:
    banner_id: int
    name: str
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetBannersActiveRow:
        return cls(
            banner_id=row["banner_id"],
            name=row["name"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetBannersTrashedRow = GetBannersActiveRow


__all__ = [
    "Banner",
    "CreateBannerRow",
    "GetBannerRow",
    "GetBannersActiveRow",
    "GetBannersRow",
    "GetBannersTrashedRow",
    "UpdateBannerRow",
]
