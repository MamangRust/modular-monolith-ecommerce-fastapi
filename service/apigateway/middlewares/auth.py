"""JWT authentication middleware. Role authorization lives in `required_role.require_roles`."""

from __future__ import annotations

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from pkg.auth.token import TokenExpiredError
from shared.errors.api_error import to_http_response
from shared.errors.core import err_unauthorized

# exact matches that skip JWT entirely.
PUBLIC_PATHS = (
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/hello",
    "/api/auth/verify-code",
    "/api/auth/refresh-token",
    "/api/auth/forgot-password",
    "/api/auth/reset-password",
    "/docs/",
    "/docs",
    # FastAPI's Swagger UI fetches this schema; the gateway serves swagger
    # publicly, so the schema must be reachable without a token too.
    "/openapi.json",
    "/swagger",
    "/metrics",
    "/health",
    "/live",
    "/ready",
)

PUBLIC_PREFIXES = ("/swagger", "/metrics")


def is_public_path(path: str) -> bool:
    return path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES)


class JwtAuthMiddleware(BaseHTTPMiddleware):
    """Validate `Authorization: Bearer <token>` and set `state.user_id`. The token manager is read from `app.state.token_manager` so tests can inject their own instance; `create_app` wires the real one."""

    async def dispatch(self, request: Request, call_next):
        if is_public_path(request.url.path):
            return await call_next(request)

        manager = getattr(request.app.state, "token_manager", None)
        if manager is None:
            return to_http_response(
                err_unauthorized.with_message("invalid access token"), request
            )

        auth = request.headers.get("Authorization", "")
        token = auth[len("Bearer "):].strip() if auth.startswith("Bearer ") else ""
        if not token:
            return to_http_response(
                err_unauthorized.with_message("invalid access token"), request
            )

        try:
            subject = manager.validate_token(token)
        except TokenExpiredError:
            return to_http_response(
                err_unauthorized.with_message("token expired"), request
            )
        except jwt.InvalidTokenError:
            return to_http_response(
                err_unauthorized.with_message("invalid access token"), request
            )
        try:
            user_id = int(subject)
        except (TypeError, ValueError):
            user_id = 0
        if user_id <= 0:
            return to_http_response(
                err_unauthorized.with_message("invalid access token"), request
            )

        request.state.user_id = user_id
        return await call_next(request)


__all__ = ["PUBLIC_PATHS", "PUBLIC_PREFIXES", "JwtAuthMiddleware", "is_public_path"]
