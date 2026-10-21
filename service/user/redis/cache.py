"""Row <-> JSON helpers for the user cache.

Rows carry `datetime` values that plain JSON cannot round-trip, so the
cache stores ISO-8601 strings and rebuilds the row dataclasses on read.
`total_count` is stored alongside the page rather than per row.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.user import (
    GetActiveUsersRow,
    GetUserByIDRow,
    GetUsersRow,
)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached user payload")
    return datetime.fromisoformat(value)


def user_row_to_dict(row: GetUserByIDRow) -> dict[str, Any]:
    return {
        "user_id": row.user_id,
        "firstname": row.firstname,
        "lastname": row.lastname,
        "email": row.email,
        "password": row.password,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def user_row_from_dict(data: dict[str, Any]) -> GetUserByIDRow:
    return GetUserByIDRow(
        user_id=int(data["user_id"]),
        firstname=data["firstname"],
        lastname=data["lastname"],
        email=data["email"],
        password=data.get("password", ""),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
    )


def users_row_to_dict(row: GetUsersRow) -> dict[str, Any]:
    return {
        "user_id": row.user_id,
        "firstname": row.firstname,
        "lastname": row.lastname,
        "email": row.email,
        "password": row.password,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def users_row_from_dict(data: dict[str, Any], total_count: int) -> GetUsersRow:
    return GetUsersRow(
        user_id=int(data["user_id"]),
        firstname=data["firstname"],
        lastname=data["lastname"],
        email=data["email"],
        password=data.get("password", ""),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        total_count=total_count,
    )


def active_row_to_dict(row: GetActiveUsersRow) -> dict[str, Any]:
    return {
        "user_id": row.user_id,
        "firstname": row.firstname,
        "lastname": row.lastname,
        "email": row.email,
        "password": row.password,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
        "deleted_at": _iso(row.deleted_at),
    }


def active_row_from_dict(data: dict[str, Any], total_count: int) -> GetActiveUsersRow:
    return GetActiveUsersRow(
        user_id=int(data["user_id"]),
        firstname=data["firstname"],
        lastname=data["lastname"],
        email=data["email"],
        password=data.get("password", ""),
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt(data.get("deleted_at")),
        total_count=total_count,
    )


__all__ = [
    "active_row_from_dict",
    "active_row_to_dict",
    "user_row_from_dict",
    "user_row_to_dict",
    "users_row_from_dict",
    "users_row_to_dict",
]
