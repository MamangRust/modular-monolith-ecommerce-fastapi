"""User query REST routes. the group is `/api/user-query` and, unlike role, it applies no `RequireRoles` middleware — only the global JWT check protects these routes."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.user.handler import UserHandler
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.domain.response.user import UserResponse, UserResponseDeleteAt

router = APIRouter(prefix="/api/user-query", tags=["user-query"])


def get_user_handler(request: Request) -> UserHandler:
    return UserHandler(request.app.state.connections)


@router.get("")
async def find_all_user(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[UserResponse]]:
    return await get_user_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_user(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[UserResponseDeleteAt]]:
    return await get_user_handler(request).find_by_active(page, page_size, search)


@router.get("/trashed")
async def find_trashed_user(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[UserResponseDeleteAt]]:
    return await get_user_handler(request).find_by_trashed(page, page_size, search)


@router.get("/{user_id}")
async def find_user_by_id(
    request: Request,
    user_id: int,
) -> ApiResponse[UserResponse]:
    return await get_user_handler(request).find_by_id(user_id)


__all__ = ["router"]
