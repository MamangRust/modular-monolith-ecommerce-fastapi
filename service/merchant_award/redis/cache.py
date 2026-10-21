"""Row <-> JSON helpers for the merchant_award caches.

Award rows carry `date` (issue/expiry) and `datetime` (created/updated/deleted)
values plus nullable strings that plain JSON cannot round-trip, so the cache
stores ISO-8601 strings and rebuilds the row dataclasses on read. `total_count`
is stored alongside the page rather than per row (see the query cache).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pkg.database.schema.merchant_award import (
    GetMerchantCertificationOrAwardRow,
    GetMerchantCertificationsAndAwardsActiveRow,
    GetMerchantCertificationsAndAwardsRow,
)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _iso_date(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached merchant award payload")
    return datetime.fromisoformat(value)


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _base_fields(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "merchant_certification_id": int(data["merchant_certification_id"]),
        "merchant_id": int(data["merchant_id"]),
        "title": data["title"],
        "description": data.get("description"),
        "issued_by": data.get("issued_by"),
        "issue_date": _date(data.get("issue_date")),
        "expiry_date": _date(data.get("expiry_date")),
        "certificate_url": data.get("certificate_url"),
        "created_at": _dt_required(data.get("created_at")),
        "updated_at": _dt_required(data.get("updated_at")),
    }


def _base_to_dict(row: Any) -> dict[str, Any]:
    return {
        "merchant_certification_id": row.merchant_certification_id,
        "merchant_id": row.merchant_id,
        "title": row.title,
        "description": row.description,
        "issued_by": row.issued_by,
        "issue_date": _iso_date(row.issue_date),
        "expiry_date": _iso_date(row.expiry_date),
        "certificate_url": row.certificate_url,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


# ---- list rows (FindAll) ----


def award_row_to_dict(row: GetMerchantCertificationsAndAwardsRow) -> dict[str, Any]:
    return {
        **_base_to_dict(row),
        "merchant_name": row.merchant_name,
    }


def award_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetMerchantCertificationsAndAwardsRow:
    return GetMerchantCertificationsAndAwardsRow(
        **_base_fields(data),
        merchant_name=data["merchant_name"],
        total_count=total_count,
    )


# ---- active/trashed rows (carry deleted_at) ----


def award_active_row_to_dict(
    row: GetMerchantCertificationsAndAwardsActiveRow,
) -> dict[str, Any]:
    return {
        **_base_to_dict(row),
        "deleted_at": _iso(row.deleted_at),
        "merchant_name": row.merchant_name,
    }


def award_active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetMerchantCertificationsAndAwardsActiveRow:
    return GetMerchantCertificationsAndAwardsActiveRow(
        **_base_fields(data),
        deleted_at=_dt(data.get("deleted_at")),
        merchant_name=data["merchant_name"],
        total_count=total_count,
    )


# ---- single row (FindById) ----


def award_by_id_to_dict(row: GetMerchantCertificationOrAwardRow) -> dict[str, Any]:
    return _base_to_dict(row)


def award_by_id_from_dict(data: dict[str, Any]) -> GetMerchantCertificationOrAwardRow:
    return GetMerchantCertificationOrAwardRow(**_base_fields(data))


# ---- page envelopes (shared by the query caches) ----


def encode_page(rows: list, total: int, to_dict) -> dict[str, Any]:
    return {"data": [to_dict(row) for row in rows], "total_records": total}


def decode_page(payload: Any, from_dict) -> tuple[list, int] | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    total = int(payload.get("total_records") or 0)
    return [from_dict(item, total) for item in data], total


__all__ = [
    "award_active_row_from_dict",
    "award_active_row_to_dict",
    "award_by_id_from_dict",
    "award_by_id_to_dict",
    "award_row_from_dict",
    "award_row_to_dict",
    "decode_page",
    "encode_page",
]
