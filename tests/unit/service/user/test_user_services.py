"""Unit tests for user query/command services, hashing and cache invalidation."""

from __future__ import annotations

from datetime import datetime

from pkg.database.schema.user import (
    CreateUserRow,
    GetActiveUsersRow,
    GetUserByEmailRow,
    GetUserByIDRow,
    GetUsersRow,
    TrashUserRow,
    UpdateUserRow,
)
from pkg.hash import Hasher
from pkg.logger.logger import Logger
from service.user.service.user_command_service import UserCommandServiceImpl
from service.user.service.user_query_service import (
    UserQueryServiceImpl,
    normalize_pagination,
)
from shared.errors import AppError, err_user_not_found_repo
from shared.observability import Observability

CREATED = datetime(2026, 1, 1, 10, 0, 0)
UPDATED = datetime(2026, 1, 2, 10, 0, 0)
DELETED = datetime(2026, 2, 3, 10, 0, 0)


def _user_row(user_id: int = 1) -> GetUserByIDRow:
    return GetUserByIDRow(user_id, "John", "Doe", "john@example.com", "h", CREATED, UPDATED)


def _users_row(user_id: int = 1, total: int = 1) -> GetUsersRow:
    return GetUsersRow(user_id, "John", "Doe", "john@example.com", "h", CREATED, UPDATED, total)


def _active_row(user_id: int = 1, total: int = 1, deleted=None) -> GetActiveUsersRow:
    return GetActiveUsersRow(
        user_id, "John", "Doe", "john@example.com", "h", CREATED, UPDATED, deleted, total
    )


def _create_row(user_id: int = 9) -> CreateUserRow:
    return CreateUserRow(
        user_id, "John", "Doe", "john@example.com", "h", "verify", CREATED, UPDATED
    )


def _update_row(user_id: int = 9) -> UpdateUserRow:
    return UpdateUserRow(user_id, "John", "Doe", "john@example.com", "h", CREATED, UPDATED)


class FakeQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.by_email: GetUserByEmailRow | None = None
        self.users = [_users_row()]
        self.active = [_active_row()]

    async def find_all(self, search, page, page_size):
        self.calls.append(f"find_all:{search}:{page}:{page_size}")
        return self.users

    async def find_by_id(self, user_id):
        self.calls.append(f"find_by_id:{user_id}")
        return _user_row(user_id)

    async def find_by_email(self, email):
        self.calls.append(f"find_by_email:{email}")
        if self.by_email is None:
            raise err_user_not_found_repo
        return self.by_email

    async def find_active(self, search, page, page_size):
        self.calls.append(f"find_active:{search}:{page}:{page_size}")
        return self.active

    async def find_trashed(self, search, page, page_size):
        self.calls.append(f"find_trashed:{search}:{page}:{page_size}")
        return self.active


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict = {}
        self.writes: list[str] = []

    async def get_users(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_users(self, page, page_size, search, users, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (users, total)

    async def get_user_by_id(self, user_id):
        return self.store.get(f"id:{user_id}")

    async def set_user_by_id(self, user):
        self.writes.append(f"id:{user.user_id}")
        self.store[f"id:{user.user_id}"] = user

    async def get_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_active(self, page, page_size, search, users, total):
        self.store[f"active:{page}:{page_size}:{search}"] = (users, total)

    async def get_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_trashed(self, page, page_size, search, users, total):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (users, total)


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.create_password: str | None = None
        self.update_password: str | None = None

    async def create(self, firstname, lastname, email, hashed_password):
        self.calls.append(f"create:{email}")
        self.create_password = hashed_password
        return _create_row()

    async def update(self, user_id, firstname, lastname, email, hashed_password):
        self.calls.append(f"update:{user_id}:{email}")
        self.update_password = hashed_password
        return _update_row(user_id)

    async def trash(self, user_id):
        self.calls.append(f"trash:{user_id}")
        return TrashUserRow(user_id, "John", "Doe", "john@example.com", CREATED, UPDATED, DELETED)

    async def restore(self, user_id):
        self.calls.append(f"restore:{user_id}")
        return TrashUserRow(user_id, "John", "Doe", "john@example.com", CREATED, UPDATED, None)

    async def delete_permanent(self, user_id):
        self.calls.append(f"delete:{user_id}")

    async def restore_all(self):
        self.calls.append("restore_all")

    async def delete_all_permanent(self):
        self.calls.append("delete_all")


class FakeCommandCache:
    def __init__(self) -> None:
        self.invalidated: list[int] = []
        self.list_invalidations = 0

    async def delete_cached_user(self, user_id):
        return 1

    async def invalidate_lists(self):
        self.list_invalidations += 1
        return 1

    async def invalidate_user(self, user_id):
        self.invalidated.append(user_id)
        return 1

    async def invalidate_all(self):
        self.list_invalidations += 1
        return 1


class FakeHasher(Hasher):
    def hash_password(self, password: str) -> str:
        return f"hashed:{password}"


def _logger() -> Logger:
    return Logger("test", "error")


def _query_service(repo, cache) -> UserQueryServiceImpl:
    return UserQueryServiceImpl(repo, cache, _logger(), Observability("test", _logger()))


def _command_service(query_repo, command_repo, cache) -> UserCommandServiceImpl:
    return UserCommandServiceImpl(
        query_repo,
        command_repo,
        cache,
        FakeHasher(),
        _logger(),
        Observability("test", _logger()),
    )


# ---- query ----


async def test_normalize_pagination() -> None:
    assert normalize_pagination(0, 0) == (1, 10)
    assert normalize_pagination(-3, -1) == (1, 10)
    assert normalize_pagination(2, 25) == (2, 25)


async def test_find_all_normalizes_and_caches() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    rows, total = await service.find_all("", 0, 0)

    assert repo.calls == ["find_all::1:10"]
    assert cache.writes == ["all:1:10:"]
    assert total == 1
    assert rows[0].total_count == 1


async def test_find_all_served_from_cache() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)
    await service.find_all("", 1, 10)
    repo.calls.clear()

    rows, total = await service.find_all("", 1, 10)

    assert repo.calls == []
    assert total == 1


async def test_find_by_id_caches_result() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    user = await service.find_by_id(5)

    assert user.user_id == 5
    assert "id:5" in cache.writes
    repo.calls.clear()
    await service.find_by_id(5)
    assert repo.calls == []


async def test_find_active_reads_cache() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)
    cache.store["active:1:10:"] = ([_active_row(total=1)], 1)

    rows, total = await service.find_active("", 1, 10)

    assert repo.calls == []
    assert total == 1


# ---- command ----


async def test_create_hashes_password_and_invalidates_lists() -> None:
    query, command, cache = FakeQueryRepo(), FakeCommandRepo(), FakeCommandCache()
    service = _command_service(query, command, cache)

    user = await service.create("John", "Doe", "john@example.com", "secret1")

    assert user.user_id == 9
    assert command.create_password == "hashed:secret1"
    assert cache.list_invalidations == 1


async def test_create_rejects_duplicate_email() -> None:
    query, command, cache = FakeQueryRepo(), FakeCommandRepo(), FakeCommandCache()
    query.by_email = GetUserByEmailRow(1, "john@example.com")
    service = _command_service(query, command, cache)

    try:
        await service.create("John", "Doe", "john@example.com", "secret1")
    except AppError as exc:
        assert exc.code == 409
        assert exc.message == "User email already exists"
    else:  # pragma: no cover
        raise AssertionError("expected conflict")

    assert command.calls == []


async def test_update_hashes_password_not_plaintext() -> None:
    """Deviation fix: persisted the plaintext password on update."""
    query, command, cache = FakeQueryRepo(), FakeCommandRepo(), FakeCommandCache()
    service = _command_service(query, command, cache)

    await service.update(1, "John", "Doe", "john@example.com", "secret1")

    assert command.update_password == "hashed:secret1"
    assert cache.invalidated == [1]


async def test_update_rejects_duplicate_email() -> None:
    query, command, cache = FakeQueryRepo(), FakeCommandRepo(), FakeCommandCache()
    query.by_email = GetUserByEmailRow(2, "taken@example.com")
    service = _command_service(query, command, cache)

    try:
        await service.update(1, "John", "Doe", "taken@example.com", "secret1")
    except AppError as exc:
        assert exc.code == 409
    else:  # pragma: no cover
        raise AssertionError("expected conflict")

    assert command.calls == []


async def test_trash_restore_delete_invalidate() -> None:
    query, command, cache = FakeQueryRepo(), FakeCommandRepo(), FakeCommandCache()
    service = _command_service(query, command, cache)

    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)

    assert cache.invalidated == [2, 2, 2]


async def test_bulk_commands_invalidate_lists() -> None:
    query, command, cache = FakeQueryRepo(), FakeCommandRepo(), FakeCommandCache()
    service = _command_service(query, command, cache)

    await service.restore_all()
    await service.delete_all_permanent()

    assert cache.list_invalidations == 2
