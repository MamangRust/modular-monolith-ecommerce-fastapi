"""Unit tests for the auth services (in-process, no server/DB). Covers the login lockout policy, registration (hash + role + code), the password-reset flow (including the cache-key deviation), verification-code handling and refresh-token rotation."""

from __future__ import annotations

import time
from datetime import datetime, timedelta

import jwt
import pytest

from pkg.auth import new_manager
from pkg.database.schema.auth import (
    AuthCreateUserRow,
    GetResetTokenRow,
    GetUserByEmailAndVerifiedRow,
    GetUserByVerificationCodeRow,
    RefreshToken,
    UpdateUserIsVerifiedRow,
)
from pkg.database.schema.role import Role
from pkg.database.schema.user import GetUserByEmailRow, GetUserByIDRow
from pkg.hash import Hasher, InvalidCredentialsError
from pkg.logger.logger import Logger
from service.auth.redis.common import RESET_TOKEN_TTL, VERIFY_CODE_TTL
from service.auth.service.identity_service import IdentityServiceImpl
from service.auth.service.login_service import LoginServiceImpl
from service.auth.service.password_reset_service import PasswordResetServiceImpl
from service.auth.service.register_service import RegisterServiceImpl
from service.auth.service.token_service import TokenService
from shared.domain.requests.auth import (
    AuthRequest,
    CreateRefreshToken,
    CreateResetPasswordRequest,
    CreateResetTokenRequest,
    RegisterRequest,
    UpdateRefreshToken,
)
from shared.errors import (
    AppError,
    err_account_locked,
    err_failed_password_no_match,
    err_user_email_already,
    err_user_not_found_repo,
    err_user_not_found_res,
)
from shared.observability import Observability

CREATED = datetime(2026, 1, 1, 10, 0, 0)
UPDATED = datetime(2026, 1, 2, 10, 0, 0)
SECRET = "unit-test-secret-key-0123456789abcdef"


def _logger() -> Logger:
    return Logger("test", "error")


def _expired_token(user_id: int) -> str:
    """A well-formed HS256 token whose `exp` is an hour in the past."""
    now = int(time.time())
    return jwt.encode(
        {
            "sub": str(user_id),
            "aud": "refresh",
            "iat": now - 7200,
            "exp": now - 3600,
        },
        SECRET,
        algorithm="HS256",
    )


def _obs() -> Observability:
    return Observability("test", _logger())


class FakeHasher(Hasher):
    """`secret1` is the only accepted password."""

    def __init__(self) -> None:
        self.hashed: list[str] = []

    def hash_password(self, password: str) -> str:
        self.hashed.append(password)
        return f"hashed:{password}"

    def compare_password(self, hashed: str, password: str) -> None:
        if password != "secret1":
            raise InvalidCredentialsError("invalid credentials")


# ---- fakes: repositories ----


class FakeUserRepo:
    def __init__(self) -> None:
        self.by_email: GetUserByEmailRow | None = None
        self.email_error: AppError | None = None
        self.verified_user: GetUserByEmailAndVerifiedRow | None = (
            GetUserByEmailAndVerifiedRow(
                1, "John", "Doe", "john@example.com", "hashed:secret1", CREATED, UPDATED
            )
        )
        self.by_code: GetUserByVerificationCodeRow | None = None
        self.created: RegisterRequest | None = None
        self.verified_updates: list[tuple[int, bool]] = []
        self.password_updates: list[tuple[int, str]] = []

    async def find_by_id(self, user_id):
        return GetUserByIDRow(
            user_id, "John", "Doe", "john@example.com", "h", CREATED, UPDATED
        )

    async def find_by_email(self, email):
        if self.email_error is not None:
            raise self.email_error
        if self.by_email is None:
            raise err_user_not_found_repo
        return self.by_email

    async def find_by_email_and_verify(self, email):
        if self.verified_user is None:
            raise err_user_not_found_repo
        return self.verified_user

    async def find_by_verification_code(self, verification_code):
        return self.by_code

    async def create_user(self, request):
        self.created = request
        return AuthCreateUserRow(
            9,
            request.firstname,
            request.lastname,
            request.email,
            request.password,
            CREATED,
            UPDATED,
        )

    async def update_user_is_verified(self, user_id, is_verified):
        self.verified_updates.append((user_id, is_verified))
        return UpdateUserIsVerifiedRow(
            user_id, "John", "Doe", "john@example.com", "h", CREATED, UPDATED
        )

    async def update_user_password(self, user_id, password):
        self.password_updates.append((user_id, password))
        return UpdateUserIsVerifiedRow(
            user_id, "John", "Doe", "john@example.com", password, CREATED, UPDATED
        )


class FakeRoleRepo:
    def __init__(self, role: Role | None = None) -> None:
        self.role = role or Role(5, "ROLE_ADMIN", CREATED, UPDATED, None)
        self.names: list[str] = []

    async def find_by_id(self, role_id):
        return self.role

    async def find_by_name(self, name):
        self.names.append(name)
        return self.role


class FakeUserRoleRepo:
    def __init__(self) -> None:
        self.assigned: list[tuple[int, int]] = []

    async def assign_role_to_user(self, request):
        self.assigned.append((request.user_id, request.role_id))
        return None

    async def remove_role_from_user(self, request):
        return None


class FakeResetTokenRepo:
    def __init__(self) -> None:
        self.requests: list[CreateResetTokenRequest] = []
        self.deleted: list[int] = []
        self.by_token: GetResetTokenRow | None = None

    async def find_by_token(self, code):
        if self.by_token is None:
            raise AppError("NOT_FOUND", 404, "Reset Token not found")
        return self.by_token

    async def create_reset_token(self, request):
        self.requests.append(request)
        return GetResetTokenRow(request.user_id, request.reset_token, CREATED)

    async def delete_reset_token(self, user_id):
        self.deleted.append(user_id)


class FakeRefreshTokenRepo:
    def __init__(self) -> None:
        self.created: list[CreateRefreshToken] = []
        self.updated: list[UpdateRefreshToken] = []
        self.deleted_by_token: list[str] = []
        self.deleted_by_user: list[int] = []
        self.by_token: RefreshToken | None = None
        self.by_user: RefreshToken | None = None

    async def find_by_token(self, token):
        assert self.by_token is not None
        return self.by_token

    async def find_by_user_id(self, user_id):
        assert self.by_user is not None
        return self.by_user

    async def create_refresh_token(self, request):
        self.created.append(request)
        return RefreshToken(
            1, request.user_id, request.token, CREATED, CREATED, UPDATED, None
        )

    async def update_refresh_token(self, request):
        self.updated.append(request)
        return RefreshToken(
            1, request.user_id, request.token, CREATED, CREATED, UPDATED, None
        )

    async def delete_refresh_token(self, token):
        self.deleted_by_token.append(token)

    async def delete_refresh_token_by_user_id(self, user_id):
        self.deleted_by_user.append(user_id)


# ---- fakes: caches ----


class FakeLoginCache:
    def __init__(self, locked: bool = False) -> None:
        self.locked = locked
        self.incremented: list[str] = []
        self.reset: list[str] = []

    async def get_cached_login(self, email):
        return None

    async def set_cached_login(self, email, data, ttl_seconds):
        return None

    async def increment_failed_login(self, email):
        self.incremented.append(email)
        return len(self.incremented)

    async def reset_failed_login(self, email):
        self.reset.append(email)

    async def is_account_locked(self, email):
        return self.locked


class FakeRegisterCache:
    def __init__(self) -> None:
        self.codes: list[tuple[str, str, int]] = []

    async def set_verification_code_cache(self, email, code, ttl_seconds):
        self.codes.append((email, code, ttl_seconds))


class FakePasswordResetCache:
    def __init__(self, cached: tuple[int, bool] = (0, False)) -> None:
        self.cached = cached
        self.set_calls: list[tuple[str, int, int]] = []
        self.deleted: list[str] = []
        self.deleted_codes: list[str] = []

    async def set_reset_token_cache(self, token, user_id, ttl_seconds):
        self.set_calls.append((token, user_id, ttl_seconds))

    async def get_reset_token_cache(self, token):
        return self.cached

    async def delete_reset_token_cache(self, token):
        self.deleted.append(token)

    async def delete_verification_code_cache(self, email):
        self.deleted_codes.append(email)


class FakeIdentityCache:
    def __init__(self, cached: tuple[str, bool] = ("", False)) -> None:
        self.cached = cached
        self.stored: list[tuple[str, int]] = []
        self.deleted: list[str] = []
        self.user_info: dict[int, GetUserByIDRow] = {}
        self.set_user_info: list[int] = []

    async def set_refresh_token(self, token, ttl_seconds):
        self.stored.append((token, ttl_seconds))

    async def get_refresh_token(self, token):
        return self.cached

    async def delete_refresh_token(self, token):
        self.deleted.append(token)

    async def set_cached_user_info(self, user, ttl_seconds):
        self.set_user_info.append(user.user_id)
        self.user_info[user.user_id] = user

    async def get_cached_user_info(self, user_id):
        return self.user_info.get(int(user_id))

    async def delete_cached_user_info(self, user_id):
        self.user_info.pop(int(user_id), None)


def _token_service(repo: FakeRefreshTokenRepo) -> TokenService:
    return TokenService(new_manager(SECRET), repo, _logger(), _obs())


def _login_service(user, cache, hasher, token_service) -> LoginServiceImpl:
    return LoginServiceImpl(cache, user, hasher, token_service, _logger(), _obs())


def _register_service(user, role, user_role, cache, hasher) -> RegisterServiceImpl:
    return RegisterServiceImpl(
        cache, user, role, user_role, hasher, _logger(), _obs()
    )


def _reset_service(cache, user, reset_token, hasher) -> PasswordResetServiceImpl:
    return PasswordResetServiceImpl(
        cache, user, reset_token, hasher, _logger(), _obs()
    )


def _identity_service(cache, repo, user, token_service) -> IdentityServiceImpl:
    return IdentityServiceImpl(
        cache, new_manager(SECRET), repo, user, token_service, _logger(), _obs()
    )


# ---- token service ----


async def test_create_access_token_uses_access_audience() -> None:
    repo = FakeRefreshTokenRepo()
    service = _token_service(repo)
    manager = new_manager(SECRET)

    token = await service.create_access_token(42)

    assert manager.validate_token(token) == "42"
    assert repo.created == []  # access tokens are not persisted


async def test_create_refresh_token_replaces_existing_and_persists() -> None:
    repo = FakeRefreshTokenRepo()
    service = _token_service(repo)

    token = await service.create_refresh_token(42)

    assert new_manager(SECRET).validate_token(token) == "42"
    assert repo.deleted_by_user == [42]
    assert len(repo.created) == 1
    created = repo.created[0]
    assert created.user_id == 42
    assert created.token == token
    # layout, second precision, ~24h ahead.
    expires = datetime.strptime(created.expires_at, "%Y-%m-%d %H:%M:%S")
    assert timedelta(hours=23) < expires - datetime.now() < timedelta(hours=25)


# ---- login ----


async def test_login_rejects_locked_account_without_touching_repo() -> None:
    user, cache = FakeUserRepo(), FakeLoginCache(locked=True)
    service = _login_service(user, cache, FakeHasher(), _token_service(FakeRefreshTokenRepo()))

    with pytest.raises(AppError) as excinfo:
        await service.login(AuthRequest(email="john@example.com", password="secret1"))

    assert excinfo.value.is_(err_account_locked)
    assert excinfo.value.code == 403


async def test_login_wrong_password_counts_and_fails() -> None:
    user, cache = FakeUserRepo(), FakeLoginCache()
    service = _login_service(user, cache, FakeHasher(), _token_service(FakeRefreshTokenRepo()))

    with pytest.raises(AppError) as excinfo:
        await service.login(AuthRequest(email="john@example.com", password="wrongpw"))

    assert excinfo.value.is_(err_failed_password_no_match)
    assert excinfo.value.code == 401
    assert cache.incremented == ["john@example.com"]
    assert cache.reset == []


async def test_login_success_issues_tokens_and_clears_failures() -> None:
    user, cache = FakeUserRepo(), FakeLoginCache()
    repo = FakeRefreshTokenRepo()
    service = _login_service(user, cache, FakeHasher(), _token_service(repo))

    tokens = await service.login(
        AuthRequest(email="john@example.com", password="secret1")
    )

    assert new_manager(SECRET).validate_token(tokens.access_token) == "1"
    assert new_manager(SECRET).validate_token(tokens.refresh_token) == "1"
    assert cache.reset == ["john@example.com"]
    assert repo.deleted_by_user == [1]
    assert len(repo.created) == 1


async def test_login_unverified_user_is_not_found() -> None:
    user, cache = FakeUserRepo(), FakeLoginCache()
    user.verified_user = None
    service = _login_service(user, cache, FakeHasher(), _token_service(FakeRefreshTokenRepo()))

    with pytest.raises(AppError) as excinfo:
        await service.login(AuthRequest(email="john@example.com", password="secret1"))

    assert excinfo.value.code == 404


# ---- register ----


async def test_register_hashes_password_assigns_role_and_caches_code() -> None:
    user, role, user_role = FakeUserRepo(), FakeRoleRepo(), FakeUserRoleRepo()
    cache, hasher = FakeRegisterCache(), FakeHasher()
    service = _register_service(user, role, user_role, cache, hasher)

    created = await service.register(
        RegisterRequest(
            firstname="John",
            lastname="Doe",
            email="john@example.com",
            password="secret1",
            confirm_password="secret1",
        )
    )

    assert created.user_id == 9
    assert user.created is not None
    assert user.created.password == "hashed:secret1"
    assert len(user.created.verified_code) == 10
    assert user.created.verified_code.isalnum()
    assert user.created.is_verified is False
    assert role.names == ["ROLE_ADMIN"]
    assert user_role.assigned == [(9, 5)]
    assert cache.codes == [
        ("john@example.com", user.created.verified_code, VERIFY_CODE_TTL)
    ]


async def test_register_rejects_existing_email() -> None:
    user, role, user_role = FakeUserRepo(), FakeRoleRepo(), FakeUserRoleRepo()
    user.by_email = GetUserByEmailRow(1, "john@example.com")
    service = _register_service(user, role, user_role, FakeRegisterCache(), FakeHasher())

    with pytest.raises(AppError) as excinfo:
        await service.register(
            RegisterRequest(
                firstname="John",
                lastname="Doe",
                email="john@example.com",
                password="secret1",
                confirm_password="secret1",
            )
        )

    assert excinfo.value.is_(err_user_email_already)
    assert excinfo.value.code == 409
    assert user.created is None
    assert user_role.assigned == []


async def test_register_treats_lookup_error_as_email_free() -> None:
    """only rejects when the lookup *succeeds*; a failed lookup proceeds."""
    user, role, user_role = FakeUserRepo(), FakeRoleRepo(), FakeUserRoleRepo()
    user.email_error = AppError("INTERNAL", 500, "db down")
    service = _register_service(user, role, user_role, FakeRegisterCache(), FakeHasher())

    created = await service.register(
        RegisterRequest(
            firstname="John",
            lastname="Doe",
            email="john@example.com",
            password="secret1",
            confirm_password="secret1",
        )
    )

    assert created.user_id == 9


# ---- password reset / verification ----


async def test_forgot_password_creates_token_and_caches_by_token() -> None:
    user, reset = FakeUserRepo(), FakeResetTokenRepo()
    cache, hasher = FakePasswordResetCache(), FakeHasher()
    user.by_email = GetUserByEmailRow(3, "john@example.com")
    service = _reset_service(cache, user, reset, hasher)

    result = await service.forgot_password("john@example.com")

    assert result is True
    assert len(reset.requests) == 1
    request = reset.requests[0]
    assert request.user_id == 3
    assert len(request.reset_token) == 10
    # Deviation: keyed the *set* by user id and the *get* by token.
    assert cache.set_calls == [(request.reset_token, 3, RESET_TOKEN_TTL)]


async def test_reset_password_uses_cache_hit_and_hashes_new_password() -> None:
    user, reset = FakeUserRepo(), FakeResetTokenRepo()
    cache, hasher = FakePasswordResetCache(cached=(3, True)), FakeHasher()
    service = _reset_service(cache, user, reset, hasher)

    result = await service.reset_password(
        CreateResetPasswordRequest(
            reset_token="tok", password="secret2", confirm_password="secret2"
        )
    )

    assert result is True
    assert reset.deleted == [3]
    assert cache.deleted == ["tok"]
    # Deviation: stored the plaintext password here.
    assert user.password_updates == [(3, "hashed:secret2")]


async def test_reset_password_falls_back_to_db_on_cache_miss() -> None:
    user, reset = FakeUserRepo(), FakeResetTokenRepo()
    reset.by_token = GetResetTokenRow(7, "tok", CREATED)
    cache, hasher = FakePasswordResetCache(), FakeHasher()
    service = _reset_service(cache, user, reset, hasher)

    await service.reset_password(
        CreateResetPasswordRequest(
            reset_token="tok", password="secret2", confirm_password="secret2"
        )
    )

    assert user.password_updates == [(7, "hashed:secret2")]
    assert cache.set_calls == [("tok", 7, RESET_TOKEN_TTL)]


async def test_reset_password_rejects_mismatched_confirmation() -> None:
    user, reset = FakeUserRepo(), FakeResetTokenRepo()
    cache, hasher = FakePasswordResetCache(cached=(3, True)), FakeHasher()
    service = _reset_service(cache, user, reset, hasher)

    with pytest.raises(AppError) as excinfo:
        await service.reset_password(
            CreateResetPasswordRequest(
                reset_token="tok", password="secret2", confirm_password="other12"
            )
        )

    assert excinfo.value.code == 400
    assert excinfo.value.message == "password and confirm password do not match"
    assert user.password_updates == []


async def test_verify_code_missing_maps_to_not_found() -> None:
    """Deviation: dereferenced a nil result here and panicked."""
    user, reset = FakeUserRepo(), FakeResetTokenRepo()
    service = _reset_service(FakePasswordResetCache(), user, reset, FakeHasher())

    with pytest.raises(AppError) as excinfo:
        await service.verify_code("nope")

    assert excinfo.value.is_(err_user_not_found_res)
    assert user.verified_updates == []


async def test_verify_code_marks_verified_and_drops_cache() -> None:
    user, reset = FakeUserRepo(), FakeResetTokenRepo()
    user.by_code = GetUserByVerificationCodeRow(
        4, "John", "Doe", "john@example.com", "h", CREATED, UPDATED
    )
    cache = FakePasswordResetCache()
    service = _reset_service(cache, user, reset, FakeHasher())

    result = await service.verify_code("code-123")

    assert result is True
    assert user.verified_updates == [(4, True)]
    assert cache.deleted_codes == ["john@example.com"]


# ---- identity ----


async def test_refresh_token_rotates_and_updates_db() -> None:
    cache, repo, user = FakeIdentityCache(), FakeRefreshTokenRepo(), FakeUserRepo()
    token_service = _token_service(repo)
    service = _identity_service(cache, repo, user, token_service)
    presented = new_manager(SECRET).generate_token(8, "refresh")

    tokens = await service.refresh_token(presented)

    assert new_manager(SECRET).validate_token(tokens.access_token) == "8"
    assert cache.deleted == [presented]
    assert repo.deleted_by_token == [presented]
    assert len(repo.updated) == 1
    assert repo.updated[0].user_id == 8
    assert cache.stored and cache.stored[0][0] == tokens.refresh_token


async def test_refresh_token_expired_is_internal_and_cleans_up() -> None:
    cache, repo, user = FakeIdentityCache(), FakeRefreshTokenRepo(), FakeUserRepo()
    service = _identity_service(cache, repo, user, _token_service(repo))
    expired = _expired_token(8)

    with pytest.raises(AppError) as excinfo:
        await service.refresh_token(expired)

    assert excinfo.value.code == 500
    assert cache.deleted == [expired]
    assert repo.deleted_by_token == [expired]


async def test_refresh_token_cache_hit_skips_db_update() -> None:
    """The cached value is a JWT (bug), so a numeric hit is synthetic."""
    cache = FakeIdentityCache(cached=("8", True))
    repo, user = FakeRefreshTokenRepo(), FakeUserRepo()
    service = _identity_service(cache, repo, user, _token_service(repo))

    tokens = await service.refresh_token("cached-token")

    assert new_manager(SECRET).validate_token(tokens.access_token) == "8"
    assert cache.deleted == ["cached-token"]
    assert repo.updated == []


async def test_get_me_prefers_cache_then_populates_it() -> None:
    cache, repo, user = FakeIdentityCache(), FakeRefreshTokenRepo(), FakeUserRepo()
    service = _identity_service(cache, repo, user, _token_service(repo))

    first = await service.get_me(1)
    assert first.user_id == 1
    assert cache.set_user_info == [1]

    second = await service.get_me(1)
    assert second.user_id == 1
    assert cache.set_user_info == [1]  # still one write: second read hit cache
