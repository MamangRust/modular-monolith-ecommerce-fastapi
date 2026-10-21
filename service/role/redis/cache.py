"""Row <-> JSON helpers for the role cache.

Rows carry `datetime` values that plain JSON cannot round-trip, so the
cache stores ISO-8601 strings and rebuilds the row dataclasses on read.
`total_count` is stored alongside the page rather than per row.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.role import GetActiveRolesRow, GetRolesRow, Role


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached role payload")
    return datetime.fromisoformat(value)


def role_to_dict(role: Role) -> dict[str, Any]:
    return {
        "role_id": role.role_id,
        "role_name": role.role_name,
        "created_at": _iso(role.created_at),
        "updated_at": _iso(role.updated_at),
        "deleted_at": _iso(role.deleted_at),
    }


def role_from_dict(data: dict[str, Any]) -> Role:
    return Role(
        role_id=int(data["role_id"]),
        role_name=data["role_name"],
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt(data.get("deleted_at")),
    )


def roles_row_to_dict(row: GetRolesRow) -> dict[str, Any]:
    return {
        "role_id": row.role_id,
        "role_name": row.role_name,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def roles_row_from_dict(data: dict[str, Any], total_count: int) -> GetRolesRow:
    return GetRolesRow(
        role_id=int(data["role_id"]),
        role_name=data["role_name"],
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        total_count=total_count,
    )


def active_row_to_dict(row: GetActiveRolesRow) -> dict[str, Any]:
    return {
        "role_id": row.role_id,
        "role_name": row.role_name,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
        "deleted_at": _iso(row.deleted_at),
    }


def active_row_from_dict(data: dict[str, Any], total_count: int) -> GetActiveRolesRow:
    return GetActiveRolesRow(
        role_id=int(data["role_id"]),
        role_name=data["role_name"],
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt(data.get("deleted_at")),
        total_count=total_count,
    )


__all__ = [
    "active_row_from_dict",
    "active_row_to_dict",
    "role_from_dict",
    "role_to_dict",
    "roles_row_from_dict",
    "roles_row_to_dict",
]
