"""Row types for the merchants table. `description`/`address`/`contact_email`/`contact_phone` are nullable in (`*string`), so the row dataclasses model them as `str | None`. Timestamps surface as `datetime.datetime`; the handlers format them as `%Y-%m-%d %H:%M:%S` to match the `2006-01-02 15:04:05` layout (a new format for this domain — see the). `GetUserByIDRow` is the merchant service's *own* copy of the user read row (the `db.User` returned by `repository.UserQueryRepository`); the outbound user adapter maps the remote proto onto it."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Merchant:

    merchant_id: int
    user_id: int
    name: str
    description: str | None
    address: str | None
    contact_email: str | None
    contact_phone: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> Merchant:
        return cls(
            merchant_id=row["merchant_id"],
            user_id=row["user_id"],
            name=row["name"],
            description=row.get("description"),
            address=row.get("address"),
            contact_email=row.get("contact_email"),
            contact_phone=row.get("contact_phone"),
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateMerchantRow:
    """`Create`/`Update`/`UpdateStatus`/`FindById` projection — no `deleted_at`."""

    merchant_id: int
    user_id: int
    name: str
    description: str | None
    address: str | None
    contact_email: str | None
    contact_phone: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateMerchantRow:
        return cls(
            merchant_id=row["merchant_id"],
            user_id=row["user_id"],
            name=row["name"],
            description=row.get("description"),
            address=row.get("address"),
            contact_email=row.get("contact_email"),
            contact_phone=row.get("contact_phone"),
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


GetMerchantByIDRow = CreateMerchantRow
UpdateMerchantRow = CreateMerchantRow
UpdateMerchantStatusRow = CreateMerchantRow


@dataclass
class GetMerchantsRow:
    """`FindAll` projection with a window total count (active-only)."""

    merchant_id: int
    user_id: int
    name: str
    description: str | None
    address: str | None
    contact_email: str | None
    contact_phone: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantsRow:
        return cls(
            merchant_id=row["merchant_id"],
            user_id=row["user_id"],
            name=row["name"],
            description=row.get("description"),
            address=row.get("address"),
            contact_email=row.get("contact_email"),
            contact_phone=row.get("contact_phone"),
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetMerchantsActiveRow:
    """`FindActive`/`FindTrashed` projection: carries `deleted_at` + total."""

    merchant_id: int
    user_id: int
    name: str
    description: str | None
    address: str | None
    contact_email: str | None
    contact_phone: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantsActiveRow:
        return cls(
            merchant_id=row["merchant_id"],
            user_id=row["user_id"],
            name=row["name"],
            description=row.get("description"),
            address=row.get("address"),
            contact_email=row.get("contact_email"),
            contact_phone=row.get("contact_phone"),
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetMerchantsTrashedRow = GetMerchantsActiveRow


@dataclass
class GetUserByIDRow:
    """The merchant service's local copy of the user read row. Populated by the outbound user gRPC adapter, never by SQL: the adapter maps the remote `UserResponse` onto these fields. `password` is not on the wire and stays empty, exactly like the adapter."""

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


__all__ = [
    "CreateMerchantRow",
    "GetMerchantByIDRow",
    "GetMerchantsActiveRow",
    "GetMerchantsRow",
    "GetMerchantsTrashedRow",
    "GetUserByIDRow",
    "Merchant",
    "UpdateMerchantRow",
    "UpdateMerchantStatusRow",
]
