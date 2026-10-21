"""Row types for the auth domain. `Role` is reused from the role schema module rather than duplicated, since the auth role repository selects the same columns as the role domain."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pkg.database.schema.role import Role


@dataclass
class GetUserByEmailAndVerifiedRow:
    """`FindByEmailAndVerify` projection (verified users only)."""

    user_id: int
    firstname: str
    lastname: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetUserByEmailAndVerifiedRow:
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
class GetUserByVerificationCodeRow:
    user_id: int
    firstname: str
    lastname: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetUserByVerificationCodeRow:
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
class AuthCreateUserRow:
    """`CreateUser` projection (`db.CreateUserRow` in the auth context). Unlike the user domain's row this does not select `verification_code`, matching the auth CTE's RETURNING list."""

    user_id: int
    firstname: str
    lastname: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> AuthCreateUserRow:
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
class UpdateUserIsVerifiedRow:
    user_id: int
    firstname: str
    lastname: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> UpdateUserIsVerifiedRow:
        return cls(
            user_id=row["user_id"],
            firstname=row["firstname"],
            lastname=row["lastname"],
            email=row["email"],
            password=row.get("password", ""),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateUserPasswordRow = UpdateUserIsVerifiedRow


@dataclass
class GetResetTokenRow:
    user_id: int
    token: str
    expiry_date: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetResetTokenRow:
        return cls(
            user_id=int(row["user_id"]),
            token=row["token"],
            expiry_date=row["expiry_date"],
        )


CreateResetTokenRow = GetResetTokenRow


@dataclass
class RefreshToken:
    refresh_token_id: int
    user_id: int
    token: str
    expiration: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> RefreshToken:
        return cls(
            refresh_token_id=row["refresh_token_id"],
            user_id=row["user_id"],
            token=row["token"],
            expiration=row["expiration"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class UserRole:
    user_role_id: int
    user_id: int
    role_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> UserRole:
        return cls(
            user_role_id=row["user_role_id"],
            user_id=row["user_id"],
            role_id=row["role_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


__all__ = [
    "AuthCreateUserRow",
    "CreateResetTokenRow",
    "GetResetTokenRow",
    "GetUserByEmailAndVerifiedRow",
    "GetUserByVerificationCodeRow",
    "RefreshToken",
    "Role",
    "UpdateUserIsVerifiedRow",
    "UpdateUserPasswordRow",
    "UserRole",
]
