"""Unit tests for the gateway auth cache and its transport-level caching.

The gateway caches whole REST envelopes (login by email, refresh by token,
get-me by user id) so a repeated call is served without a gRPC round trip.
A fake Redis backs a real `CacheStore`; the gRPC stub is replaced with a fake
that counts calls.
"""

from __future__ import annotations

from typing import Any

from pkg.logger.logger import Logger
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.auth.handler import AuthHandler
from service.apigateway.redis.auth import AuthCache
from shared.cache import CacheStore
from shared.domain.response.auth import (
    ApiResponseGetMe,
    ApiResponseLogin,
    ApiResponseRefreshToken,
    TokenResponse,
)
from shared.domain.response.user import UserResponse


class FakeRedis:
    """Minimal async Redis surface used by `CacheStore`."""

    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.data.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self.data[key] = value
        return True

    async def delete(self, *keys: str) -> int:
        removed = 0
        for key in keys:
            if self.data.pop(key, None) is not None:
                removed += 1
        return removed


class FakeChannel:
    """Just enough of the grpc.aio channel surface for the generated stub."""

    def unary_unary(self, *args: Any, **kwargs: Any) -> Any:
        return lambda *a, **k: None


class FakeStub:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def LoginUser(self, request: Any, timeout: float = 0) -> Any:
        from pb.auth import auth_pb2

        self.calls.append("login")
        return auth_pb2.ApiResponseLogin(
            status="success",
            message="LoginUser successfull",
            data=auth_pb2.TokenResponse(
                access_token="access-1", refresh_token="refresh-1"
            ),
        )

    async def GetMe(self, request: Any, timeout: float = 0) -> Any:
        from pb.auth import auth_pb2

        self.calls.append("get_me")
        message = auth_pb2.ApiResponseGetMe(
            status="success", message="Get me successfully"
        )
        message.data.id = request.userId
        message.data.firstname = "John"
        message.data.lastname = "Doe"
        message.data.email = "john@example.com"
        message.data.created_at = "2026-08-19 10:00:00 +0000 UTC"
        message.data.updated_at = "2026-08-19 10:00:00 +0000 UTC"
        return message


def _logger() -> Logger:
    return Logger("test", "error")


def _cache() -> AuthCache:
    return AuthCache(CacheStore(FakeRedis(), _logger()), _logger())


def _handler(cache: AuthCache | None) -> tuple[AuthHandler, FakeStub]:
    connections = ServiceConnections(channels={"auth": FakeChannel()}, addresses={})
    handler = AuthHandler(connections, cache)
    stub = FakeStub()
    handler._client = stub
    return handler, stub


# ---- cache round-trips ----


async def test_login_envelope_round_trips() -> None:
    cache = _cache()
    envelope = ApiResponseLogin(
        status="success",
        message="LoginUser successfull",
        data=TokenResponse(access_token="a", refresh_token="r"),
    )

    await cache.set_cached_login("john@example.com", envelope)
    restored = await cache.get_cached_login("john@example.com")

    assert restored == envelope


async def test_refresh_envelope_round_trips() -> None:
    cache = _cache()
    envelope = ApiResponseRefreshToken(
        status="success",
        message="Refresh token successful",
        data=TokenResponse(access_token="a2", refresh_token="r2"),
    )

    await cache.set_refresh_token("old-token", envelope)

    assert await cache.get_refresh_token("old-token") == envelope


async def test_user_info_envelope_round_trips() -> None:
    cache = _cache()
    envelope = ApiResponseGetMe(
        status="success",
        message="Get me successfully",
        data=UserResponse(
            id=7,
            firstname="John",
            lastname="Doe",
            email="john@example.com",
            is_verified=False,
            created_at="2026-08-19 10:00:00 +0000 UTC",
            updated_at="2026-08-19 10:00:00 +0000 UTC",
        ),
    )

    await cache.set_cached_user_info(7, envelope)

    assert await cache.get_cached_user_info(7) == envelope


async def test_missing_keys_report_a_miss() -> None:
    cache = _cache()
    assert await cache.get_cached_login("nobody@example.com") is None
    assert await cache.get_refresh_token("nope") is None
    assert await cache.get_cached_user_info(404) is None


async def test_malformed_payload_reports_a_miss() -> None:
    store = CacheStore(FakeRedis(), _logger())
    cache = AuthCache(store, _logger())
    # A JSON string where a dict is expected must not raise.
    await store.set_json("auth:login:john@example.com", "not-a-dict", 60)
    assert await cache.get_cached_login("john@example.com") is None


# ---- handler caching ----


async def test_login_second_call_is_served_from_cache() -> None:
    handler, stub = _handler(_cache())

    first = await handler.login("john@example.com", "secret1")
    second = await handler.login("john@example.com", "secret1")

    assert stub.calls == ["login"]
    assert first.data.access_token == second.data.access_token == "access-1"


async def test_get_me_second_call_is_served_from_cache() -> None:
    handler, stub = _handler(_cache())

    first = await handler.get_me(7)
    second = await handler.get_me(7)

    assert stub.calls == ["get_me"]
    assert first.data.id == second.data.id == 7


async def test_handler_without_cache_always_calls_the_service() -> None:
    handler, stub = _handler(None)

    await handler.login("john@example.com", "secret1")
    await handler.login("john@example.com", "secret1")

    assert stub.calls == ["login", "login"]
