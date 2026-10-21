"""Row <-> JSON helpers for the merchant_policy caches.

Every business column is a plain `str`/`int`; only the `datetime` timestamps
(and the nullable `deleted_at`) need special handling, so the cache stores
ISO-8601 strings for them. `total_count` is stored alongside the page rather
than per row (see the query cache).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.merchant_policy import (
    GetMerchantPoliciesActiveRow,
    GetMerchantPoliciesRow,
    GetMerchantPolicyRow,
)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError(
            "required timestamp missing from cached merchant policy payload"
        )
    return datetime.fromisoformat(value)


def _base_fields(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "merchant_policy_id": int(data["merchant_policy_id"]),
        "merchant_id": int(data["merchant_id"]),
        "policy_type": data["policy_type"],
        "title": data["title"],
        "description": data["description"],
        "created_at": _dt_required(data.get("created_at")),
        "updated_at": _dt_required(data.get("updated_at")),
    }


def _base_to_dict(row: Any) -> dict[str, Any]:
    return {
        "merchant_policy_id": row.merchant_policy_id,
        "merchant_id": row.merchant_id,
        "policy_type": row.policy_type,
        "title": row.title,
        "description": row.description,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


# ---- list rows (FindAll) ----


def policy_row_to_dict(row: GetMerchantPoliciesRow) -> dict[str, Any]:
    return {
        **_base_to_dict(row),
        "merchant_name": row.merchant_name,
    }


def policy_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetMerchantPoliciesRow:
    return GetMerchantPoliciesRow(
        **_base_fields(data),
        merchant_name=data["merchant_name"],
        total_count=total_count,
    )


# ---- active/trashed rows (carry deleted_at) ----


def policy_active_row_to_dict(
    row: GetMerchantPoliciesActiveRow,
) -> dict[str, Any]:
    return {
        **_base_to_dict(row),
        "deleted_at": _iso(row.deleted_at),
        "merchant_name": row.merchant_name,
    }


def policy_active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetMerchantPoliciesActiveRow:
    return GetMerchantPoliciesActiveRow(
        **_base_fields(data),
        deleted_at=_dt(data.get("deleted_at")),
        merchant_name=data["merchant_name"],
        total_count=total_count,
    )


# ---- single row (FindById) ----


def policy_by_id_to_dict(row: GetMerchantPolicyRow) -> dict[str, Any]:
    return _base_to_dict(row)


def policy_by_id_from_dict(data: dict[str, Any]) -> GetMerchantPolicyRow:
    return GetMerchantPolicyRow(**_base_fields(data))


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
    "decode_page",
    "encode_page",
    "policy_active_row_from_dict",
    "policy_active_row_to_dict",
    "policy_by_id_from_dict",
    "policy_by_id_to_dict",
    "policy_row_from_dict",
    "policy_row_to_dict",
]
