"""Row <-> JSON helpers for the merchant_business caches.

Business rows carry nullable strings and nullable ints plus `datetime` values
that plain JSON cannot round-trip, so the cache stores ISO-8601 strings for the
timestamps and keeps the nullable scalars as-is. `total_count` is stored
alongside the page rather than per row (see the query cache).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.merchant_business import (
    GetMerchantBusinessInformationRow,
    GetMerchantsBusinessInformationActiveRow,
    GetMerchantsBusinessInformationRow,
)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError(
            "required timestamp missing from cached merchant business payload"
        )
    return datetime.fromisoformat(value)


def _base_fields(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "merchant_business_info_id": int(data["merchant_business_info_id"]),
        "merchant_id": int(data["merchant_id"]),
        "business_type": data.get("business_type"),
        "tax_id": data.get("tax_id"),
        "established_year": data.get("established_year"),
        "number_of_employees": data.get("number_of_employees"),
        "website_url": data.get("website_url"),
        "created_at": _dt_required(data.get("created_at")),
        "updated_at": _dt_required(data.get("updated_at")),
    }


def _base_to_dict(row: Any) -> dict[str, Any]:
    return {
        "merchant_business_info_id": row.merchant_business_info_id,
        "merchant_id": row.merchant_id,
        "business_type": row.business_type,
        "tax_id": row.tax_id,
        "established_year": row.established_year,
        "number_of_employees": row.number_of_employees,
        "website_url": row.website_url,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


# ---- list rows (FindAll) ----


def business_row_to_dict(
    row: GetMerchantsBusinessInformationRow,
) -> dict[str, Any]:
    return {
        **_base_to_dict(row),
        "merchant_name": row.merchant_name,
    }


def business_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetMerchantsBusinessInformationRow:
    return GetMerchantsBusinessInformationRow(
        **_base_fields(data),
        merchant_name=data["merchant_name"],
        total_count=total_count,
    )


# ---- active/trashed rows (carry deleted_at) ----


def business_active_row_to_dict(
    row: GetMerchantsBusinessInformationActiveRow,
) -> dict[str, Any]:
    return {
        **_base_to_dict(row),
        "deleted_at": _iso(row.deleted_at),
        "merchant_name": row.merchant_name,
    }


def business_active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetMerchantsBusinessInformationActiveRow:
    return GetMerchantsBusinessInformationActiveRow(
        **_base_fields(data),
        deleted_at=_dt(data.get("deleted_at")),
        merchant_name=data["merchant_name"],
        total_count=total_count,
    )


# ---- single row (FindById) ----


def business_by_id_to_dict(row: GetMerchantBusinessInformationRow) -> dict[str, Any]:
    return _base_to_dict(row)


def business_by_id_from_dict(
    data: dict[str, Any],
) -> GetMerchantBusinessInformationRow:
    return GetMerchantBusinessInformationRow(**_base_fields(data))


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
    "business_active_row_from_dict",
    "business_active_row_to_dict",
    "business_by_id_from_dict",
    "business_by_id_to_dict",
    "business_row_from_dict",
    "business_row_to_dict",
    "decode_page",
    "encode_page",
]
