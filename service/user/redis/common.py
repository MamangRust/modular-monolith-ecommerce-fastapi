"""User cache keys and TTL."""

from __future__ import annotations

USER_ALL_KEY = "user:all:page:%d:pageSize:%d:search:%s"
USER_BY_ID_KEY = "user:id:%d"
USER_ACTIVE_KEY = "user:active:page:%d:pageSize:%d:search:%s"
USER_TRASHED_KEY = "user:trashed:page:%d:pageSize:%d:search:%s"

TTL_DEFAULT = 300  # 5 minutes

# Patterns cleared after a user mutation (see UserCommandCacheImpl).
LIST_PATTERNS = (
    "user:all:page:*",
    "user:active:page:*",
    "user:trashed:page:*",
)


def user_all_key(page: int, page_size: int, search: str) -> str:
    return USER_ALL_KEY % (page, page_size, search)


def user_by_id_key(user_id: int) -> str:
    return USER_BY_ID_KEY % user_id


def user_active_key(page: int, page_size: int, search: str) -> str:
    return USER_ACTIVE_KEY % (page, page_size, search)


def user_trashed_key(page: int, page_size: int, search: str) -> str:
    return USER_TRASHED_KEY % (page, page_size, search)


__all__ = [
    "LIST_PATTERNS",
    "TTL_DEFAULT",
    "USER_ACTIVE_KEY",
    "USER_ALL_KEY",
    "USER_BY_ID_KEY",
    "USER_TRASHED_KEY",
    "user_active_key",
    "user_all_key",
    "user_by_id_key",
    "user_trashed_key",
]
