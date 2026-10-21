"""JSON helpers for the auth caches. `GetUserByIDRow` carries datetimes and `TokenResponse` is a dataclass, so both need explicit converters for Redis round-trips."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.user import GetUserByIDRow
from shared.domain.response.auth import TokenResponse


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt_required(value: str | None) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached auth payload")
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


def token_response_to_dict(token: TokenResponse) -> dict[str, str]:
    return {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
    }


def token_response_from_dict(data: dict[str, Any]) -> TokenResponse:
    return TokenResponse(
        access_token=str(data.get("access_token", "")),
        refresh_token=str(data.get("refresh_token", "")),
    )


__all__ = [
    "token_response_from_dict",
    "token_response_to_dict",
    "user_row_from_dict",
    "user_row_to_dict",
]
