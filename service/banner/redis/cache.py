"""Row <-> JSON helpers for the banner cache.

Banner rows carry `date`, `time` and `datetime` values that plain JSON
cannot round-trip, so the cache stores ISO-8601 strings and rebuilds the
row dataclasses on read. `total_count` is stored alongside the page rather
than per row.
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from pkg.database.schema.banner import (
    GetBannerRow,
    GetBannersActiveRow,
    GetBannersRow,
)


def _iso_dt(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached banner payload")
    return datetime.fromisoformat(value)


def _iso_date(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _date_required(value: str | None) -> date:
    if not value:
        raise ValueError("required date missing from cached banner payload")
    return date.fromisoformat(value)


def _iso_time(value: time | None) -> str | None:
    return value.isoformat() if value is not None else None


def _time_required(value: str | None) -> time:
    if not value:
        raise ValueError("required time missing from cached banner payload")
    return time.fromisoformat(value)


def banner_row_to_dict(row: GetBannersRow | GetBannersActiveRow) -> dict[str, Any]:
    return {
        "banner_id": row.banner_id,
        "name": row.name,
        "start_date": _iso_date(row.start_date),
        "end_date": _iso_date(row.end_date),
        "start_time": _iso_time(row.start_time),
        "end_time": _iso_time(row.end_time),
        "is_active": row.is_active,
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def banner_row_from_dict(data: dict[str, Any], total_count: int) -> GetBannersRow:
    return GetBannersRow(
        banner_id=int(data["banner_id"]),
        name=data["name"],
        start_date=_date_required(data.get("start_date")),
        end_date=_date_required(data.get("end_date")),
        start_time=_time_required(data.get("start_time")),
        end_time=_time_required(data.get("end_time")),
        is_active=bool(data.get("is_active", False)),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        total_count=total_count,
    )


def active_row_to_dict(row: GetBannersActiveRow) -> dict[str, Any]:
    payload = banner_row_to_dict(row)
    payload["deleted_at"] = _iso_dt(row.deleted_at)
    return payload


def active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetBannersActiveRow:
    return GetBannersActiveRow(
        banner_id=int(data["banner_id"]),
        name=data["name"],
        start_date=_date_required(data.get("start_date")),
        end_date=_date_required(data.get("end_date")),
        start_time=_time_required(data.get("start_time")),
        end_time=_time_required(data.get("end_time")),
        is_active=bool(data.get("is_active", False)),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt(data.get("deleted_at")),
        total_count=total_count,
    )


def banner_by_id_to_dict(row: GetBannerRow) -> dict[str, Any]:
    return {
        "banner_id": row.banner_id,
        "name": row.name,
        "start_date": _iso_date(row.start_date),
        "end_date": _iso_date(row.end_date),
        "start_time": _iso_time(row.start_time),
        "end_time": _iso_time(row.end_time),
        "is_active": row.is_active,
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def banner_by_id_from_dict(data: dict[str, Any]) -> GetBannerRow:
    return GetBannerRow(
        banner_id=int(data["banner_id"]),
        name=data["name"],
        start_date=_date_required(data.get("start_date")),
        end_date=_date_required(data.get("end_date")),
        start_time=_time_required(data.get("start_time")),
        end_time=_time_required(data.get("end_time")),
        is_active=bool(data.get("is_active", False)),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
    )


__all__ = [
    "active_row_from_dict",
    "active_row_to_dict",
    "banner_by_id_from_dict",
    "banner_by_id_to_dict",
    "banner_row_from_dict",
    "banner_row_to_dict",
]
