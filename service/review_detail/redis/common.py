"""Review detail cache keys and TTL."""

from __future__ import annotations

REVIEW_DETAIL_ALL_KEY = "review_detail:all:page:%d:pageSize:%d:search:%s"
REVIEW_DETAIL_BY_ID_KEY = "review_detail:id:%d"
REVIEW_DETAIL_ACTIVE_KEY = "review_detail:active:page:%d:pageSize:%d:search:%s"
REVIEW_DETAIL_TRASHED_KEY = "review_detail:trashed:page:%d:pageSize:%d:search:%s"

TTL_DEFAULT = 300  # 5 minutes

# Pattern cleared after a review detail mutation (see
# ReviewDetailCommandCacheImpl). flushes the entire `review_detail:*` namespace.
REVIEW_DETAIL_ALL_PATTERN = "review_detail:*"


def review_detail_all_key(page: int, page_size: int, search: str) -> str:
    return REVIEW_DETAIL_ALL_KEY % (page, page_size, search)


def review_detail_by_id_key(review_detail_id: int) -> str:
    return REVIEW_DETAIL_BY_ID_KEY % review_detail_id


def review_detail_active_key(page: int, page_size: int, search: str) -> str:
    return REVIEW_DETAIL_ACTIVE_KEY % (page, page_size, search)


def review_detail_trashed_key(page: int, page_size: int, search: str) -> str:
    return REVIEW_DETAIL_TRASHED_KEY % (page, page_size, search)


__all__ = [
    "REVIEW_DETAIL_ACTIVE_KEY",
    "REVIEW_DETAIL_ALL_KEY",
    "REVIEW_DETAIL_ALL_PATTERN",
    "REVIEW_DETAIL_BY_ID_KEY",
    "REVIEW_DETAIL_TRASHED_KEY",
    "TTL_DEFAULT",
    "review_detail_active_key",
    "review_detail_all_key",
    "review_detail_by_id_key",
    "review_detail_trashed_key",
]
