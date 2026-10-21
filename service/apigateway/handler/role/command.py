"""Role command REST routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from service.apigateway.handler.role.handler import RoleHandler
from service.apigateway.middlewares.required_role import require_roles
from shared.domain.response.responses import ApiResponse
from shared.domain.response.role import RoleResponse

router = APIRouter(prefix="/api/role", tags=["role-command"])

ROLE_COMMAND_ADMIN = "Admin_Admin_14"

require_command_admin = require_roles(ROLE_COMMAND_ADMIN)


class RoleNameBody(BaseModel):
    name: str = Field(..., min_length=1)


def get_role_handler(request: Request) -> RoleHandler:
    return RoleHandler(request.app.state.connections)


@router.post("")
async def create_role(
    request: Request,
    body: RoleNameBody,
    roles: list[str] = Depends(require_command_admin),
) -> ApiResponse[RoleResponse]:
    return await get_role_handler(request).create(body.name)


@router.post("/restore/all")
async def restore_all_role(
    request: Request,
    roles: list[str] = Depends(require_command_admin),
) -> ApiResponse[None]:
    return await get_role_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_role_permanent(
    request: Request,
    roles: list[str] = Depends(require_command_admin),
) -> ApiResponse[None]:
    return await get_role_handler(request).delete_all_permanent()


@router.post("/trashed/{role_id}")
async def trash_role(
    request: Request,
    role_id: int,
    roles: list[str] = Depends(require_command_admin),
) -> ApiResponse[RoleResponse]:
    return await get_role_handler(request).trash(role_id)


@router.put("/restore/{role_id}")
async def restore_role(
    request: Request,
    role_id: int,
    roles: list[str] = Depends(require_command_admin),
) -> ApiResponse[RoleResponse]:
    return await get_role_handler(request).restore(role_id)


@router.delete("/permanent/{role_id}")
async def delete_role_permanent(
    request: Request,
    role_id: int,
    roles: list[str] = Depends(require_command_admin),
) -> ApiResponse[None]:
    return await get_role_handler(request).delete_permanent(role_id)


@router.delete("/{role_id}")
async def delete_role(
    request: Request,
    role_id: int,
    roles: list[str] = Depends(require_command_admin),
) -> ApiResponse[None]:
    return await get_role_handler(request).delete_permanent(role_id)


@router.post("/{role_id}")
async def update_role(
    request: Request,
    role_id: int,
    body: RoleNameBody,
    roles: list[str] = Depends(require_command_admin),
) -> ApiResponse[RoleResponse]:
    return await get_role_handler(request).update(role_id, body.name)


__all__ = ["ROLE_COMMAND_ADMIN", "router"]
