"""Row types for the merchant_policies table. All business columns are `NOT NULL` in the DDL (`policy_type`, `title`, `description`), so there are no nullable string/int fields here — only `deleted_at` is nullable."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class MerchantPolicy:

    merchant_policy_id: int
    merchant_id: int
    policy_type: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> MerchantPolicy:
        return cls(
            merchant_policy_id=row["merchant_policy_id"],
            merchant_id=row["merchant_id"],
            policy_type=row["policy_type"],
            title=row["title"],
            description=row["description"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateMerchantPolicyRow:
    """`Create`/`Update` projection — base columns, no `deleted_at`."""

    merchant_policy_id: int
    merchant_id: int
    policy_type: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateMerchantPolicyRow:
        return cls(
            merchant_policy_id=row["merchant_policy_id"],
            merchant_id=row["merchant_id"],
            policy_type=row["policy_type"],
            title=row["title"],
            description=row["description"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateMerchantPolicyRow = CreateMerchantPolicyRow


@dataclass
class GetMerchantPolicyRow:
    """Single `GetMerchantPolicy` projection — base only."""

    merchant_policy_id: int
    merchant_id: int
    policy_type: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantPolicyRow:
        return cls(
            merchant_policy_id=row["merchant_policy_id"],
            merchant_id=row["merchant_id"],
            policy_type=row["policy_type"],
            title=row["title"],
            description=row["description"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class GetMerchantPoliciesRow:
    """`GetMerchantPolicies` (FindAll) projection with window total count."""

    merchant_policy_id: int
    merchant_id: int
    policy_type: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    merchant_name: str
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantPoliciesRow:
        return cls(
            merchant_policy_id=row["merchant_policy_id"],
            merchant_id=row["merchant_id"],
            policy_type=row["policy_type"],
            title=row["title"],
            description=row["description"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            merchant_name=row["merchant_name"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetMerchantPoliciesActiveRow:
    """`GetMerchantPoliciesActive`/`...Trashed` projection: `deleted_at` + total."""

    merchant_policy_id: int
    merchant_id: int
    policy_type: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    merchant_name: str
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantPoliciesActiveRow:
        return cls(
            merchant_policy_id=row["merchant_policy_id"],
            merchant_id=row["merchant_id"],
            policy_type=row["policy_type"],
            title=row["title"],
            description=row["description"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            merchant_name=row["merchant_name"],
            total_count=int(row["total_count"]),
        )


GetMerchantPoliciesTrashedRow = GetMerchantPoliciesActiveRow


__all__ = [
    "CreateMerchantPolicyRow",
    "GetMerchantPoliciesActiveRow",
    "GetMerchantPoliciesRow",
    "GetMerchantPoliciesTrashedRow",
    "GetMerchantPolicyRow",
    "MerchantPolicy",
    "UpdateMerchantPolicyRow",
]
