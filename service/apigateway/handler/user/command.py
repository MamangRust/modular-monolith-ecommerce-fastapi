"""User command REST routes. Route names follow the *registered* routes (`/permanent/:id`, `/restore/all`,...), not the stale swagger annotations in that file which document `/delete/{id}` and `/delete/all`."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.user.handler import UserHandler
from shared.domain.requests.user import CreateUserRequest, UpdateUserRequest
from shared.domain.response.responses import ApiResponse
from shared.domain.response.user import UserResponse, UserResponseDeleteAt

router = APIRouter(prefix="/api/user-command", tags=["user-command"])


def get_user_handler(request: Request) -> UserHandler:
    return UserHandler(request.app.state.connections)


@router.post("/create")
async def create_user(
    request: Request,
    body: CreateUserRequest,
) -> ApiResponse[UserResponse]:
    return await get_user_handler(request).create(
        body.firstname,
        body.lastname,
        body.email,
        body.password,
        body.confirm_password,
    )


# Static paths are registered before the `{user_id}` ones: Starlette matches
# in order, so `/restore/all` would otherwise be captured as user_id="all".
@router.post("/restore/all")
async def restore_all_user(request: Request) -> ApiResponse[None]:
    return await get_user_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_user_permanent(request: Request) -> ApiResponse[None]:
    return await get_user_handler(request).delete_all_permanent()


@router.post("/update/{user_id}")
async def update_user(
    request: Request,
    user_id: int,
    body: UpdateUserRequest,
) -> ApiResponse[UserResponse]:
    return await get_user_handler(request).update(
        user_id,
        body.firstname,
        body.lastname,
        body.email,
        body.password,
        body.confirm_password,
    )


@router.post("/trashed/{user_id}")
async def trash_user(
    request: Request,
    user_id: int,
) -> ApiResponse[UserResponseDeleteAt]:
    return await get_user_handler(request).trash(user_id)


@router.post("/restore/{user_id}")
async def restore_user(
    request: Request,
    user_id: int,
) -> ApiResponse[UserResponseDeleteAt]:
    return await get_user_handler(request).restore(user_id)


@router.delete("/permanent/{user_id}")
async def delete_user_permanent(
    request: Request,
    user_id: int,
) -> ApiResponse[None]:
    return await get_user_handler(request).delete_permanent(user_id)


__all__ = ["router"]
