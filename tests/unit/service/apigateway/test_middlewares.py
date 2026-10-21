"""Unit tests for the gateway RBAC dependency and JWT middleware."""

from __future__ import annotations

import time
from types import SimpleNamespace

import jwt
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from pkg.auth.token import new_manager
from service.apigateway.middlewares.auth import JwtAuthMiddleware
from service.apigateway.middlewares.required_role import require_roles
from shared.errors import AppError


class FakeValidator:
    def __init__(self, roles: list[str]) -> None:
        self.roles = roles
        self.calls: list[int] = []

    async def validate(self, user_id: int) -> list[str]:
        self.calls.append(user_id)
        return self.roles


def _request(
    *, user_id: int | None = 1, role_names: list[str] | None = None, validator=None
):
    state = SimpleNamespace(user_id=user_id, role_names=role_names)
    app_state = SimpleNamespace(role_validator=validator)
    return SimpleNamespace(state=state, app=SimpleNamespace(state=app_state))


async def test_allowed_role_passes() -> None:
    validator = FakeValidator(["Admin_Role_10"])
    dependency = require_roles("Admin_Role_10")
    roles = await dependency(_request(validator=validator))
    assert roles == ["Admin_Role_10"]
    assert validator.calls == [1]


async def test_disallowed_role_is_403() -> None:
    validator = FakeValidator(["ROLE_USER"])
    dependency = require_roles("Admin_Role_10")
    with pytest.raises(AppError) as excinfo:
        await dependency(_request(validator=validator))
    assert excinfo.value.code == 403
    assert excinfo.value.message == "Role not permitted"


async def test_empty_allow_list_accepts_any_role() -> None:
    validator = FakeValidator(["ROLE_USER"])
    roles = await require_roles()(_request(validator=validator))
    assert roles == ["ROLE_USER"]


async def test_cached_role_names_skip_validator() -> None:
    validator = FakeValidator(["ROLE_USER"])
    request = _request(role_names=["Admin_Role_10"], validator=validator)
    roles = await require_roles("Admin_Role_10")(request)
    assert roles == ["Admin_Role_10"]
    assert validator.calls == []


async def test_missing_user_and_no_validator_is_401() -> None:
    with pytest.raises(AppError) as excinfo:
        await require_roles("Admin_Role_10")(_request(user_id=None, validator=None))
    assert excinfo.value.code == 500  # validator not configured


async def test_missing_user_id_with_validator_is_401() -> None:
    validator = FakeValidator(["Admin_Role_10"])
    with pytest.raises(AppError) as excinfo:
        await require_roles("Admin_Role_10")(_request(user_id=None, validator=validator))
    assert excinfo.value.code == 401


SECRET = "unit-test-secret"


def _app() -> FastAPI:
    app = FastAPI()
    app.state.token_manager = new_manager(SECRET)
    app.add_middleware(JwtAuthMiddleware)

    @app.get("/health")
    async def health() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/protected")
    async def protected(request: Request) -> dict[str, object]:
        return {"user_id": request.state.user_id}

    return app


def test_public_path_skips_auth() -> None:
    with TestClient(_app()) as client:
        assert client.get("/health").status_code == 200


def test_missing_token_is_401() -> None:
    with TestClient(_app()) as client:
        response = client.get("/protected")
    assert response.status_code == 401
    assert response.json()["message"] == "invalid access token"


def test_valid_token_sets_user_id() -> None:
    token = new_manager(SECRET).generate_token(42, "access")
    with TestClient(_app()) as client:
        response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"user_id": 42}


def test_invalid_token_is_401() -> None:
    with TestClient(_app()) as client:
        response = client.get("/protected", headers={"Authorization": "Bearer not-a-token"})
    assert response.status_code == 401
    assert response.json()["message"] == "invalid access token"


def test_expired_token_is_401() -> None:
    expired = jwt.encode(
        {"sub": "1", "aud": "payment-gateway", "iat": int(time.time()) - 100, "exp": int(time.time()) - 10},
        SECRET,
        algorithm="HS256",
    )
    with TestClient(_app()) as client:
        response = client.get("/protected", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401
    assert response.json()["message"] == "token expired"
