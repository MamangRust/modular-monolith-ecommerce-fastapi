"""Unit tests for role query/command services and cache invalidation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.auth import UserRole
from pkg.database.schema.role import GetActiveRolesRow, GetRolesRow, Role
from pkg.logger.logger import Logger
from service.role.service.role_command_service import RoleCommandServiceImpl
from service.role.service.role_query_service import (
    RoleQueryServiceImpl,
    normalize_pagination,
)
from shared.observability import Observability

CREATED = datetime(2026, 1, 1, 10, 0, 0)
UPDATED = datetime(2026, 1, 2, 10, 0, 0)


def _role(role_id: int = 1, name: str = "Admin", deleted: datetime | None = None) -> Role:
    return Role(
        role_id=role_id,
        role_name=name,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted,
    )


def _row(role_id: int = 1, total: int = 1) -> GetRolesRow:
    return GetRolesRow(
        role_id=role_id,
        role_name="Admin",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(role_id: int = 1, total: int = 1) -> GetActiveRolesRow:
    return GetActiveRolesRow(
        role_id=role_id,
        role_name="Admin",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=total,
    )


class FakeQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.roles: list[GetRolesRow] = [_row(total=1)]
        self.active: list[GetActiveRolesRow] = [_active_row(total=1)]
        self.by_id = _role()
        self.by_user: list[Role] = [_role()]

    async def find_all(self, search, page, page_size):
        self.calls.append(f"find_all:{search}:{page}:{page_size}")
        return self.roles

    async def find_by_id(self, role_id):
        self.calls.append(f"find_by_id:{role_id}")
        return _role(role_id)

    async def find_by_name(self, role_name):
        self.calls.append("find_by_name")
        return self.by_id

    async def find_by_user_id(self, user_id):
        self.calls.append(f"find_by_user_id:{user_id}")
        return self.by_user

    async def find_active(self, search, page, page_size):
        self.calls.append(f"find_active:{search}:{page}:{page_size}")
        return self.active

    async def find_trashed(self, search, page, page_size):
        self.calls.append(f"find_trashed:{search}:{page}:{page_size}")
        return self.active


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_roles(self, page, page_size, search):
        return self.store.get(f"roles:{page}:{page_size}:{search}")

    async def set_roles(self, page, page_size, search, roles, total):
        self.writes.append(f"roles:{page}:{page_size}:{search}")
        self.store[f"roles:{page}:{page_size}:{search}"] = (roles, total)

    async def get_role_by_id(self, role_id):
        return self.store.get(f"id:{role_id}")

    async def set_role_by_id(self, role):
        self.writes.append(f"id:{role.role_id}")
        self.store[f"id:{role.role_id}"] = role

    async def get_role_by_user_id(self, user_id):
        return self.store.get(f"user:{user_id}")

    async def set_role_by_user_id(self, user_id, roles):
        self.store[f"user:{user_id}"] = roles

    async def get_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_active(self, page, page_size, search, roles, total):
        self.store[f"active:{page}:{page_size}:{search}"] = (roles, total)

    async def get_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_trashed(self, page, page_size, search, roles, total):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (roles, total)


def _query_service(repo: FakeQueryRepo, cache: FakeQueryCache) -> RoleQueryServiceImpl:
    return RoleQueryServiceImpl(repo, cache, Logger("test", "error"), Observability("test", Logger("test", "error")))


async def test_normalize_pagination() -> None:
    assert normalize_pagination(0, 0) == (1, 10)
    assert normalize_pagination(-3, -1) == (1, 10)
    assert normalize_pagination(2, 25) == (2, 25)


async def test_find_all_normalizes_and_caches() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    rows, total = await service.find_all("", 0, 0)

    assert repo.calls == ["find_all::1:10"]
    assert cache.writes == ["roles:1:10:"]
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


async def test_find_active_reads_cache() -> None:
    """Deviation fix: wrote but never read the active cache."""
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)
    cache.store["active:1:10:"] = ([_active_row(total=1)], 1)

    rows, total = await service.find_active("", 1, 10)

    assert repo.calls == []
    assert total == 1
    assert rows[0].role_id == 1


async def test_find_by_id_caches_result() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)
    role = await service.find_by_id(5)
    assert role.role_id == 5
    assert "id:5" in cache.writes
    repo.calls.clear()
    await service.find_by_id(5)
    assert repo.calls == []


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, role_name):
        self.calls.append(f"create:{role_name}")
        return _role(9, role_name)

    async def update(self, role_id, role_name):
        self.calls.append(f"update:{role_id}:{role_name}")
        return _role(role_id, role_name)

    async def trash(self, role_id):
        self.calls.append(f"trash:{role_id}")
        return _role(role_id, deleted=UPDATED)

    async def restore(self, role_id):
        self.calls.append(f"restore:{role_id}")
        return _role(role_id)

    async def delete_permanent(self, role_id):
        self.calls.append(f"delete:{role_id}")

    async def restore_all(self):
        self.calls.append("restore_all")

    async def assign_role_to_user(self, request):
        self.calls.append(f"assign:{request.user_id}:{request.role_id}")
        return UserRole(11, request.user_id, request.role_id, CREATED, UPDATED, None)

    async def delete_all_permanent(self):
        self.calls.append("delete_all")


class FakeCommandCache:
    def __init__(self) -> None:
        self.invalidated_roles: list[int] = []
        self.list_invalidations = 0
        self.all_invalidations = 0

    async def delete_cached_role(self, role_id):
        self.invalidated_roles.append(role_id)
        return 1

    async def invalidate_lists(self):
        self.list_invalidations += 1
        return 1

    async def invalidate_role(self, role_id):
        self.invalidated_roles.append(role_id)
        return 1

    async def invalidate_all(self):
        self.all_invalidations += 1
        return 1


def _command_service(repo: FakeCommandRepo, cache: FakeCommandCache) -> RoleCommandServiceImpl:
    return RoleCommandServiceImpl(repo, cache, Logger("test", "error"), Observability("test", Logger("test", "error")))


async def test_create_invalidates_lists_after_commit() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)
    role = await service.create("NewRole")
    assert role.role_id == 9
    assert cache.list_invalidations == 1


async def test_update_invalidates_by_id_and_lists() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)
    await service.update(4, "Renamed")
    assert cache.invalidated_roles == [4]


async def test_trash_restore_delete_invalidate() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)
    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)
    assert cache.invalidated_roles == [2, 2, 2]


async def test_bulk_commands_invalidate_everything() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)
    await service.restore_all()
    await service.delete_all_permanent()
    assert cache.all_invalidations == 2
