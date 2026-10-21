"""Row types for the roles table."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Role:
    role_id: int
    role_name: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> Role:
        return cls(
            role_id=row["role_id"],
            role_name=row["role_name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class GetRolesRow:
    role_id: int
    role_name: str
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetRolesRow:
        return cls(
            role_id=row["role_id"],
            role_name=row["role_name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetActiveRolesRow:
    role_id: int
    role_name: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetActiveRolesRow:
        return cls(
            role_id=row["role_id"],
            role_name=row["role_name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetTrashedRolesRow = GetActiveRolesRow
