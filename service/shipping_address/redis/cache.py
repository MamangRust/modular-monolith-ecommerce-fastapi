"""Row <-> JSON helpers for the shipping address cache.

Shipping rows carry `datetime` values that plain JSON cannot round-trip and a
`shipping_cost` that PostgreSQL returns as `Decimal`, so the cache stores
ISO-8601 strings and a float cost, then rebuilds the row dataclasses on read.
`total_count` is stored alongside the page rather than per row (the paginated
projections all carry it).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.shipping_address import (
    GetShippingAddressActiveRow,
    GetShippingAddressByOrderIDRow,
    GetShippingAddressRow,
    GetShippingByIDRow,
)


def _iso_dt(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError(
            "required timestamp missing from cached shipping address payload"
        )
    return datetime.fromisoformat(value)


def shipping_row_to_dict(
    row: GetShippingAddressRow | GetShippingAddressActiveRow,
) -> dict[str, Any]:
    return {
        "shipping_address_id": row.shipping_address_id,
        "order_id": row.order_id,
        "alamat": row.alamat,
        "provinsi": row.provinsi,
        "negara": row.negara,
        "kota": row.kota,
        "courier": row.courier,
        "shipping_method": row.shipping_method,
        "shipping_cost": float(row.shipping_cost),
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def shipping_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetShippingAddressRow:
    return GetShippingAddressRow(
        shipping_address_id=int(data["shipping_address_id"]),
        order_id=int(data["order_id"]),
        alamat=data["alamat"],
        provinsi=data["provinsi"],
        negara=data["negara"],
        kota=data["kota"],
        courier=data["courier"],
        shipping_method=data["shipping_method"],
        shipping_cost=float(data["shipping_cost"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        total_count=total_count,
    )


def active_row_to_dict(row: GetShippingAddressActiveRow) -> dict[str, Any]:
    payload = shipping_row_to_dict(row)
    payload["deleted_at"] = _iso_dt(row.deleted_at)
    return payload


def active_row_from_dict(
    data: dict[str, Any], total_count: int
) -> GetShippingAddressActiveRow:
    return GetShippingAddressActiveRow(
        shipping_address_id=int(data["shipping_address_id"]),
        order_id=int(data["order_id"]),
        alamat=data["alamat"],
        provinsi=data["provinsi"],
        negara=data["negara"],
        kota=data["kota"],
        courier=data["courier"],
        shipping_method=data["shipping_method"],
        shipping_cost=float(data["shipping_cost"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt(data.get("deleted_at")),
        total_count=total_count,
    )


def by_id_row_to_dict(row: GetShippingByIDRow) -> dict[str, Any]:
    return {
        "shipping_address_id": row.shipping_address_id,
        "order_id": row.order_id,
        "alamat": row.alamat,
        "provinsi": row.provinsi,
        "negara": row.negara,
        "kota": row.kota,
        "courier": row.courier,
        "shipping_method": row.shipping_method,
        "shipping_cost": float(row.shipping_cost),
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def by_id_row_from_dict(data: dict[str, Any]) -> GetShippingByIDRow:
    return GetShippingByIDRow(
        shipping_address_id=int(data["shipping_address_id"]),
        order_id=int(data["order_id"]),
        alamat=data["alamat"],
        provinsi=data["provinsi"],
        negara=data["negara"],
        kota=data["kota"],
        courier=data["courier"],
        shipping_method=data["shipping_method"],
        shipping_cost=float(data["shipping_cost"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
    )


def by_order_row_to_dict(row: GetShippingAddressByOrderIDRow) -> dict[str, Any]:
    return {
        "shipping_address_id": row.shipping_address_id,
        "order_id": row.order_id,
        "alamat": row.alamat,
        "provinsi": row.provinsi,
        "negara": row.negara,
        "kota": row.kota,
        "courier": row.courier,
        "shipping_method": row.shipping_method,
        "shipping_cost": float(row.shipping_cost),
        "created_at": _iso_dt(row.created_at),
        "updated_at": _iso_dt(row.updated_at),
    }


def by_order_row_from_dict(data: dict[str, Any]) -> GetShippingAddressByOrderIDRow:
    return GetShippingAddressByOrderIDRow(
        shipping_address_id=int(data["shipping_address_id"]),
        order_id=int(data["order_id"]),
        alamat=data["alamat"],
        provinsi=data["provinsi"],
        negara=data["negara"],
        kota=data["kota"],
        courier=data["courier"],
        shipping_method=data["shipping_method"],
        shipping_cost=float(data["shipping_cost"]),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
    )


__all__ = [
    "active_row_from_dict",
    "active_row_to_dict",
    "by_id_row_from_dict",
    "by_id_row_to_dict",
    "by_order_row_from_dict",
    "by_order_row_to_dict",
    "shipping_row_from_dict",
    "shipping_row_to_dict",
]
