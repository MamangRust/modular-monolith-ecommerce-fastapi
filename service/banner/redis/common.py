"""Banner cache keys and TTL."""

from __future__ import annotations

BANNER_ALL_KEY = "banner:all:page:%d:pageSize:%d:search:%s"
BANNER_BY_ID_KEY = "banner:id:%d"
BANNER_ACTIVE_KEY = "banner:active:page:%d:pageSize:%d:search:%s"
BANNER_TRASHED_KEY = "banner:trashed:page:%d:pageSize:%d:search:%s"

TTL_DEFAULT = 300  # 5 minutes

# Patterns cleared after a banner mutation (see BannerCommandCacheImpl).
# only dropped `banner:id:*` and never invalidated lists
# invalidates both so a write is immediately visible (see Planning.md).
LIST_PATTERNS = (
    "banner:all:page:*",
    "banner:active:page:*",
    "banner:trashed:page:*",
)


def banner_all_key(page: int, page_size: int, search: str) -> str:
    return BANNER_ALL_KEY % (page, page_size, search)


def banner_by_id_key(banner_id: int) -> str:
    return BANNER_BY_ID_KEY % banner_id


def banner_active_key(page: int, page_size: int, search: str) -> str:
    return BANNER_ACTIVE_KEY % (page, page_size, search)


def banner_trashed_key(page: int, page_size: int, search: str) -> str:
    return BANNER_TRASHED_KEY % (page, page_size, search)


__all__ = [
    "BANNER_ACTIVE_KEY",
    "BANNER_ALL_KEY",
    "BANNER_BY_ID_KEY",
    "BANNER_TRASHED_KEY",
    "LIST_PATTERNS",
    "TTL_DEFAULT",
    "banner_active_key",
    "banner_all_key",
    "banner_by_id_key",
    "banner_trashed_key",
]
