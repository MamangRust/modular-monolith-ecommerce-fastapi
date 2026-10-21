"""Role query REST routes. Deviation from the source (recorded in the matrix): `GET /api/role-query/active` was wired to `FindAllRole`; here it calls `FindByActive` so the endpoint returns what its name promises."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from service.apigateway.handler.role.handler import RoleHandler
from service.apigateway.middlewares.required_role import require_roles
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.domain.response.role import RoleResponse, RoleResponseDeleteAt

router = APIRouter(prefix="/api/role-query", tags=["role-query"])

ROLE_QUERY_ADMIN = "Admin_Role_10"

require_query_admin = require_roles(ROLE_QUERY_ADMIN)


def get_role_handler(request: Request) -> RoleHandler:
    return RoleHandler(request.app.state.connections)


@router.get("")
async def find_all_role(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
    roles: list[str] = Depends(require_query_admin),
) -> APIResponsePagination[list[RoleResponse]]:
    return await get_role_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_role(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
    roles: list[str] = Depends(require_query_admin),
) -> APIResponsePagination[list[RoleResponseDeleteAt]]:
    return await get_role_handler(request).find_by_active(page, page_size, search)


@router.get("/trashed")
async def find_trashed_role(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
    roles: list[str] = Depends(require_query_admin),
) -> APIResponsePagination[list[RoleResponseDeleteAt]]:
    return await get_role_handler(request).find_by_trashed(page, page_size, search)


@router.get("/user/{user_id}")
async def find_role_by_user_id(
    request: Request,
    user_id: int,
    roles: list[str] = Depends(require_query_admin),
) -> ApiResponse[list[RoleResponse]]:
    return await get_role_handler(request).find_by_user_id(user_id)


@router.get("/{role_id}")
async def find_role_by_id(
    request: Request,
    role_id: int,
    roles: list[str] = Depends(require_query_admin),
) -> ApiResponse[RoleResponse]:
    return await get_role_handler(request).find_by_id(role_id)


__all__ = ["ROLE_QUERY_ADMIN", "router"]
