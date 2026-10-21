"""Row <-> JSON helpers for the merchant_detail caches.

Detail rows carry `datetime` values (and nullable string columns) that plain
JSON cannot round-trip, so the cache stores ISO-8601 strings and rebuilds the
row dataclasses on read. `total_count` is stored alongside the page rather than
per row (see the query cache).

`social_media_links` is kept as the decoded JSON value (a list of dicts, or
`[null]` when the LEFT JOIN matched nothing) and round-trips through JSON
unchanged. It is never projected onto the wire."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.merchant_detail import (
    GetMerchantDetailRow,
    GetMerchantDetailsActiveRow,
    GetMerchantDetailsRow,
)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError(
            "required timestamp missing from cached merchant detail payload"
        )
    return datetime.fromisoformat(value)


def _base_fields(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "merchant_detail_id": int(data["merchant_detail_id"]),
        "merchant_id": int(data["merchant_id"]),
        "display_name": data.get("display_name"),
        "cover_image_url": data.get("cover_image_url"),
        "logo_url": data.get("logo_url"),
        "short_description": data.get("short_description"),
        "website_url": data.get("website_url"),
        "created_at": _dt_required(data.get("created_at")),
        "updated_at": _dt_required(data.get("updated_at")),
    }


# ---- list rows (FindAll) ----


def detail_row_to_dict(row: GetMerchantDetailsRow) -> dict[str, Any]:
    return {
        "merchant_detail_id": row.merchant_detail_id,
        "merchant_id": row.merchant_id,
        "display_name": row.display_name,
        "cover_image_url": row.cover_image_url,
        "logo_url": row.logo_url,
        "short_description": row.short_description,
        "website_url": row.website_url,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
        "merchant_name": row.merchant_name,
        "social_media_links": row.social_media_links,
    }


def detail_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetMerchantDetailsRow:
    return GetMerchantDetailsRow(
        **_base_fields(data),
        merchant_name=data["merchant_name"],
        total_count=total_count,
        social_media_links=data.get("social_media_links"),
    )


# ---- active/trashed rows (carry deleted_at) ----


def detail_active_row_to_dict(row: GetMerchantDetailsActiveRow) -> dict[str, Any]:
    return {
        "merchant_detail_id": row.merchant_detail_id,
        "merchant_id": row.merchant_id,
        "display_name": row.display_name,
        "cover_image_url": row.cover_image_url,
        "logo_url": row.logo_url,
        "short_description": row.short_description,
        "website_url": row.website_url,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
        "deleted_at": _iso(row.deleted_at),
        "merchant_name": row.merchant_name,
        "social_media_links": row.social_media_links,
    }


def detail_active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetMerchantDetailsActiveRow:
    return GetMerchantDetailsActiveRow(
        **_base_fields(data),
        deleted_at=_dt(data.get("deleted_at")),
        merchant_name=data["merchant_name"],
        total_count=total_count,
        social_media_links=data.get("social_media_links"),
    )


# ---- single row (FindById) ----


def detail_by_id_to_dict(row: GetMerchantDetailRow) -> dict[str, Any]:
    return {
        "merchant_detail_id": row.merchant_detail_id,
        "merchant_id": row.merchant_id,
        "display_name": row.display_name,
        "cover_image_url": row.cover_image_url,
        "logo_url": row.logo_url,
        "short_description": row.short_description,
        "website_url": row.website_url,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
        "merchant_name": row.merchant_name,
        "social_media_links": row.social_media_links,
    }


def detail_by_id_from_dict(data: dict[str, Any]) -> GetMerchantDetailRow:
    return GetMerchantDetailRow(
        **_base_fields(data),
        merchant_name=data["merchant_name"],
        social_media_links=data.get("social_media_links"),
    )


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
    "detail_active_row_from_dict",
    "detail_active_row_to_dict",
    "detail_by_id_from_dict",
    "detail_by_id_to_dict",
    "detail_row_from_dict",
    "detail_row_to_dict",
    "encode_page",
]
