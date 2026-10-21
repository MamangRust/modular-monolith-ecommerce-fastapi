"""Row <-> JSON helpers for the merchant caches.

Merchant and document rows carry `datetime` values (and nullable
description/note fields) that plain JSON cannot round-trip, so the cache
stores ISO-8601 strings and rebuilds the row dataclasses on read. `total_count`
is stored alongside the page rather than per row (see the query caches).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.merchant import (
    GetMerchantByIDRow,
    GetMerchantsActiveRow,
    GetMerchantsRow,
)
from pkg.database.schema.merchant_document import (
    GetActiveMerchantDocumentsRow,
    GetMerchantDocumentRow,
    GetMerchantDocumentsRow,
)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached merchant payload")
    return datetime.fromisoformat(value)


# ---- merchant ----


def merchant_row_to_dict(row: GetMerchantsRow | GetMerchantsActiveRow) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "merchant_id": row.merchant_id,
        "user_id": row.user_id,
        "name": row.name,
        "description": row.description,
        "address": row.address,
        "contact_email": row.contact_email,
        "contact_phone": row.contact_phone,
        "status": row.status,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }
    deleted_at = getattr(row, "deleted_at", None)
    if deleted_at is not None:
        payload["deleted_at"] = _iso(deleted_at)
    return payload


def _merchant_fields(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "merchant_id": int(data["merchant_id"]),
        "user_id": int(data["user_id"]),
        "name": data["name"],
        "description": data.get("description"),
        "address": data.get("address"),
        "contact_email": data.get("contact_email"),
        "contact_phone": data.get("contact_phone"),
        "status": data["status"],
        "created_at": _dt_required(data.get("created_at")),
        "updated_at": _dt_required(data.get("updated_at")),
    }


def merchant_row_from_dict(data: dict[str, Any], total_count: int) -> GetMerchantsRow:
    return GetMerchantsRow(**_merchant_fields(data), total_count=total_count)


def merchant_active_row_to_dict(row: GetMerchantsActiveRow) -> dict[str, Any]:
    payload = merchant_row_to_dict(row)
    payload["deleted_at"] = _iso(row.deleted_at)
    return payload


def merchant_active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetMerchantsActiveRow:
    return GetMerchantsActiveRow(
        **_merchant_fields(data),
        deleted_at=_dt(data.get("deleted_at")),
        total_count=total_count,
    )


def merchant_by_id_to_dict(row: GetMerchantByIDRow) -> dict[str, Any]:
    return {
        "merchant_id": row.merchant_id,
        "user_id": row.user_id,
        "name": row.name,
        "description": row.description,
        "address": row.address,
        "contact_email": row.contact_email,
        "contact_phone": row.contact_phone,
        "status": row.status,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def merchant_by_id_from_dict(data: dict[str, Any]) -> GetMerchantByIDRow:
    return GetMerchantByIDRow(**_merchant_fields(data))


# ---- merchant documents ----


def document_row_to_dict(
    row: GetMerchantDocumentsRow | GetActiveMerchantDocumentsRow,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "document_id": row.document_id,
        "merchant_id": row.merchant_id,
        "document_type": row.document_type,
        "document_url": row.document_url,
        "status": row.status,
        "note": row.note,
        "uploaded_at": _iso(row.uploaded_at),
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }
    deleted_at = getattr(row, "deleted_at", None)
    if deleted_at is not None:
        payload["deleted_at"] = _iso(deleted_at)
    return payload


def _document_fields(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_id": int(data["document_id"]),
        "merchant_id": int(data["merchant_id"]),
        "document_type": data["document_type"],
        "document_url": data["document_url"],
        "status": data["status"],
        "note": data.get("note"),
        "uploaded_at": _dt_required(data.get("uploaded_at")),
        "created_at": _dt_required(data.get("created_at")),
        "updated_at": _dt_required(data.get("updated_at")),
    }


def document_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetMerchantDocumentsRow:
    return GetMerchantDocumentsRow(**_document_fields(data), total_count=total_count)


def document_active_row_to_dict(row: GetActiveMerchantDocumentsRow) -> dict[str, Any]:
    payload = document_row_to_dict(row)
    payload["deleted_at"] = _iso(row.deleted_at)
    return payload


def document_active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetActiveMerchantDocumentsRow:
    return GetActiveMerchantDocumentsRow(
        **_document_fields(data),
        deleted_at=_dt(data.get("deleted_at")),
        total_count=total_count,
    )


def document_by_id_to_dict(row: GetMerchantDocumentRow) -> dict[str, Any]:
    return {
        "document_id": row.document_id,
        "merchant_id": row.merchant_id,
        "document_type": row.document_type,
        "document_url": row.document_url,
        "status": row.status,
        "note": row.note,
        "uploaded_at": _iso(row.uploaded_at),
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def document_by_id_from_dict(data: dict[str, Any]) -> GetMerchantDocumentRow:
    return GetMerchantDocumentRow(**_document_fields(data))


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
    "document_active_row_from_dict",
    "document_active_row_to_dict",
    "document_by_id_from_dict",
    "document_by_id_to_dict",
    "document_row_from_dict",
    "document_row_to_dict",
    "encode_page",
    "merchant_active_row_from_dict",
    "merchant_active_row_to_dict",
    "merchant_by_id_from_dict",
    "merchant_by_id_to_dict",
    "merchant_row_from_dict",
    "merchant_row_to_dict",
]
