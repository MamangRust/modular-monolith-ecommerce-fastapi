"""Role row -> response DTO mapping."""

from __future__ import annotations

from pkg.database.schema import GetActiveRolesRow, GetRolesRow, Role
from shared.convert.convert import format_date
from shared.domain.response.role import RoleResponse, RoleResponseDeleteAt


def to_role_response(row: Role | GetRolesRow) -> RoleResponse:
    return RoleResponse(
        id=row.role_id,
        name=row.role_name,
        created_at=format_date(row.created_at),
        updated_at=format_date(row.updated_at),
    )


def to_role_response_delete_at(row: GetActiveRolesRow | Role) -> RoleResponseDeleteAt:
    return RoleResponseDeleteAt(
        id=row.role_id,
        name=row.role_name,
        created_at=format_date(row.created_at),
        updated_at=format_date(row.updated_at),
        deleted_at=format_date(getattr(row, "deleted_at", None)) or None,
    )
