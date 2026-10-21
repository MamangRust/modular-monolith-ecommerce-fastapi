"""Role cache keys and TTL."""

from __future__ import annotations

ROLE_ALL_KEY = "role:all:page:%d:pageSize:%d:search:%s"
ROLE_BY_ID_KEY = "role:id:%d"
ROLE_BY_USER_ID_KEY = "role:user_id:%d"
ROLE_ACTIVE_KEY = "role:active:page:%d:pageSize:%d:search:%s"
ROLE_TRASHED_KEY = "role:trashed:page:%d:pageSize:%d:search:%s"

TTL_DEFAULT = 300  # 5 minutes

# Patterns cleared after a role mutation (see RoleCommandCacheImpl).
LIST_PATTERNS = (
    "role:all:page:*",
    "role:active:page:*",
    "role:trashed:page:*",
    "role:user_id:*",
)


def role_all_key(page: int, page_size: int, search: str) -> str:
    return ROLE_ALL_KEY % (page, page_size, search)


def role_by_id_key(role_id: int) -> str:
    return ROLE_BY_ID_KEY % role_id


def role_by_user_id_key(user_id: int) -> str:
    return ROLE_BY_USER_ID_KEY % user_id


def role_active_key(page: int, page_size: int, search: str) -> str:
    return ROLE_ACTIVE_KEY % (page, page_size, search)


def role_trashed_key(page: int, page_size: int, search: str) -> str:
    return ROLE_TRASHED_KEY % (page, page_size, search)


__all__ = [
    "LIST_PATTERNS",
    "ROLE_ACTIVE_KEY",
    "ROLE_ALL_KEY",
    "ROLE_BY_ID_KEY",
    "ROLE_BY_USER_ID_KEY",
    "ROLE_TRASHED_KEY",
    "TTL_DEFAULT",
    "role_active_key",
    "role_all_key",
    "role_by_id_key",
    "role_by_user_id_key",
    "role_trashed_key",
]
