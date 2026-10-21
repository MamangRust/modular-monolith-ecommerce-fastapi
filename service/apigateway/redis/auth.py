"""Gateway auth response cache.

The gateway caches whole REST envelopes (login, refresh, get-me) keyed by
email / refresh token / user id. `dataclasses.asdict` handles the nested
`TokenResponse` / `UserResponse` payloads; reads rebuild the dataclasses
explicitly so callers get the same types the mapper returns.

These keys are distinct from the auth service's own cache
(`identity:refresh_token:` / `identity:user_info:`), so the two caches do
not interfere."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from pkg.logger.logger import Logger
from service.apigateway.redis.common import (
    AUTH_TTL,
    auth_login_key,
    auth_refresh_token_key,
    auth_user_info_key,
)
from shared.cache import CacheStore
from shared.domain.response.auth import (
    ApiResponseGetMe,
    ApiResponseLogin,
    ApiResponseRefreshToken,
    TokenResponse,
)
from shared.domain.response.user import UserResponse


def _token_from_dict(data: Any) -> TokenResponse:
    if not isinstance(data, dict):
        return TokenResponse(access_token="", refresh_token="")
    return TokenResponse(
        access_token=str(data.get("access_token", "")),
        refresh_token=str(data.get("refresh_token", "")),
    )


def _user_from_dict(data: Any) -> UserResponse:
    if not isinstance(data, dict):
        return UserResponse(
            id=0,
            firstname="",
            lastname="",
            email="",
            is_verified=False,
            created_at="",
            updated_at="",
        )
    return UserResponse(
        id=int(data.get("id", 0)),
        firstname=str(data.get("firstname", "")),
        lastname=str(data.get("lastname", "")),
        email=str(data.get("email", "")),
        is_verified=bool(data.get("is_verified", False)),
        created_at=str(data.get("created_at", "")),
        updated_at=str(data.get("updated_at", "")),
    )


class AuthCache:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    # ---- login ----

    async def get_cached_login(self, email: str) -> ApiResponseLogin | None:
        payload = await self._store.get_json(auth_login_key(email))
        if not isinstance(payload, dict):
            return None
        return ApiResponseLogin(
            status=str(payload.get("status", "")),
            message=str(payload.get("message", "")),
            data=_token_from_dict(payload.get("data")),
        )

    async def set_cached_login(self, email: str, data: ApiResponseLogin) -> None:
        await self._store.set_json(auth_login_key(email), asdict(data), AUTH_TTL)

    # ---- refresh token ----

    async def get_refresh_token(self, token: str) -> ApiResponseRefreshToken | None:
        payload = await self._store.get_json(auth_refresh_token_key(token))
        if not isinstance(payload, dict):
            return None
        return ApiResponseRefreshToken(
            status=str(payload.get("status", "")),
            message=str(payload.get("message", "")),
            data=_token_from_dict(payload.get("data")),
        )

    async def set_refresh_token(
        self, token: str, data: ApiResponseRefreshToken
    ) -> None:
        await self._store.set_json(
            auth_refresh_token_key(token), asdict(data), AUTH_TTL
        )

    # ---- user info ----

    async def get_cached_user_info(self, user_id: int | str) -> ApiResponseGetMe | None:
        payload = await self._store.get_json(auth_user_info_key(user_id))
        if not isinstance(payload, dict):
            return None
        return ApiResponseGetMe(
            status=str(payload.get("status", "")),
            message=str(payload.get("message", "")),
            data=_user_from_dict(payload.get("data")),
        )

    async def set_cached_user_info(
        self, user_id: int | str, data: ApiResponseGetMe
    ) -> None:
        await self._store.set_json(
            auth_user_info_key(user_id), asdict(data), AUTH_TTL
        )


__all__ = ["AuthCache"]
