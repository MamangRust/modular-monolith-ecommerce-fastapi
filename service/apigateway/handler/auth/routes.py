"""Auth REST routes. All eight routes live under `/api/auth`. `GET /hello` returns plain text (`c.String(200, "Hello")`), and `POST /register` returns **201 Created** while the rest return 200. `GET /me` reads the JWT subject the middleware stored on `request.state.user_id`; a missing subject is a 400, matching `c.Get("userId")` check. The request bodies are validated by pydantic and rendered through the shared `RequestValidationError` handler, so a bad payload yields the same 400 validation envelope as `NewValidationError`."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

from service.apigateway.handler.auth.handler import AuthHandler
from service.apigateway.redis.auth import AuthCache
from shared.domain.requests.auth import (
    AuthRequest,
    ForgotPasswordRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    VerifyCodeRequest,
)
from shared.domain.requests.user import CreateUserRequest
from shared.domain.response.auth import (
    ApiResponseForgotPassword,
    ApiResponseGetMe,
    ApiResponseLogin,
    ApiResponseRefreshToken,
    ApiResponseRegister,
    ApiResponseResetPassword,
    ApiResponseVerifyCode,
)
from shared.errors import new_bad_request_error

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_handler(request: Request) -> AuthHandler:
    cache_store = getattr(request.app.state, "cache_store", None)
    cache = AuthCache(cache_store, request.app.state.logger) if cache_store else None
    return AuthHandler(request.app.state.connections, cache)


@router.get("/hello")
async def hello() -> Response:
    return Response(content="Hello", media_type="text/plain")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    body: CreateUserRequest,
) -> ApiResponseRegister:
    return await get_auth_handler(request).register(
        body.firstname,
        body.lastname,
        body.email,
        body.password,
        body.confirm_password,
    )


@router.post("/login")
async def login(request: Request, body: AuthRequest) -> ApiResponseLogin:
    return await get_auth_handler(request).login(body.email, body.password)


@router.post("/refresh-token")
async def refresh_token(
    request: Request, body: RefreshTokenRequest
) -> ApiResponseRefreshToken:
    return await get_auth_handler(request).refresh_token(body.refresh_token)


@router.get("/me")
async def get_me(request: Request) -> ApiResponseGetMe:
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise new_bad_request_error("user not authenticated")
    return await get_auth_handler(request).get_me(int(user_id))


@router.post("/verify-code")
async def verify_code(
    request: Request, body: VerifyCodeRequest
) -> ApiResponseVerifyCode:
    return await get_auth_handler(request).verify_code(body.code)


@router.post("/forgot-password")
async def forgot_password(
    request: Request, body: ForgotPasswordRequest
) -> ApiResponseForgotPassword:
    return await get_auth_handler(request).forgot_password(body.email)


@router.post("/reset-password")
async def reset_password(
    request: Request, body: ResetPasswordRequest
) -> ApiResponseResetPassword:
    return await get_auth_handler(request).reset_password(
        body.reset_token, body.password, body.confirm_password
    )


__all__ = ["router"]
