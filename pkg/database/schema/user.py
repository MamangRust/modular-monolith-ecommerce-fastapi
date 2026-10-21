"""Row types for the users table. Handlers never emit it."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class GetUsersRow:
    """`FindAllUsers` projection: active-only, with a window total count."""

    user_id: int
    firstname: str
    lastname: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetUsersRow:
        return cls(
            user_id=row["user_id"],
            firstname=row["firstname"],
            lastname=row["lastname"],
            email=row["email"],
            password=row.get("password", ""),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetActiveUsersRow:
    user_id: int
    firstname: str
    lastname: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetActiveUsersRow:
        return cls(
            user_id=row["user_id"],
            firstname=row["firstname"],
            lastname=row["lastname"],
            email=row["email"],
            password=row.get("password", ""),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetTrashedUsersRow = GetActiveUsersRow
GetUsersWithPaginationRow = GetUsersRow
GetActiveUsersWithPaginationRow = GetActiveUsersRow
GetTrashedUsersWithPaginationRow = GetActiveUsersRow


@dataclass
class GetUserByIDRow:
    user_id: int
    firstname: str
    lastname: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetUserByIDRow:
        return cls(
            user_id=row["user_id"],
            firstname=row["firstname"],
            lastname=row["lastname"],
            email=row["email"],
            password=row.get("password", ""),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class GetUserByEmailRow:
    user_id: int
    email: str

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetUserByEmailRow:
        return cls(user_id=row["user_id"], email=row["email"])


@dataclass
class CreateUserRow:
    user_id: int
    firstname: str
    lastname: str
    email: str
    password: str
    verification_code: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateUserRow:
        return cls(
            user_id=row["user_id"],
            firstname=row["firstname"],
            lastname=row["lastname"],
            email=row["email"],
            password=row.get("password", ""),
            verification_code=row.get("verification_code", ""),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class UpdateUserRow:
    user_id: int
    firstname: str
    lastname: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> UpdateUserRow:
        return cls(
            user_id=row["user_id"],
            firstname=row["firstname"],
            lastname=row["lastname"],
            email=row["email"],
            password=row.get("password", ""),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class TrashUserRow:
    user_id: int
    firstname: str
    lastname: str
    email: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> TrashUserRow:
        return cls(
            user_id=row["user_id"],
            firstname=row["firstname"],
            lastname=row["lastname"],
            email=row["email"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


RestoreUserRow = TrashUserRow


__all__ = [
    "CreateUserRow",
    "GetActiveUsersRow",
    "GetActiveUsersWithPaginationRow",
    "GetTrashedUsersRow",
    "GetTrashedUsersWithPaginationRow",
    "GetUserByEmailRow",
    "GetUserByIDRow",
    "GetUsersRow",
    "GetUsersWithPaginationRow",
    "RestoreUserRow",
    "TrashUserRow",
    "UpdateUserRow",
]
