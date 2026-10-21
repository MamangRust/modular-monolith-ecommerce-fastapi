"""Slider cache keys and TTL."""

from __future__ import annotations

SLIDER_ALL_KEY = "slider:all:page:%d:pageSize:%d:search:%s"
SLIDER_BY_ID_KEY = "slider:id:%d"
SLIDER_ACTIVE_KEY = "slider:active:page:%d:pageSize:%d:search:%s"
SLIDER_TRASHED_KEY = "slider:trashed:page:%d:pageSize:%d:search:%s"

TTL_DEFAULT = 300  # 5 minutes

# Pattern cleared after a slider mutation (see SliderCommandCacheImpl).
# flushes the entire `slider:*` namespace, so uses the same
# single wildcard.
SLIDER_ALL_PATTERN = "slider:*"


def slider_all_key(page: int, page_size: int, search: str) -> str:
    return SLIDER_ALL_KEY % (page, page_size, search)


def slider_by_id_key(slider_id: int) -> str:
    return SLIDER_BY_ID_KEY % slider_id


def slider_active_key(page: int, page_size: int, search: str) -> str:
    return SLIDER_ACTIVE_KEY % (page, page_size, search)


def slider_trashed_key(page: int, page_size: int, search: str) -> str:
    return SLIDER_TRASHED_KEY % (page, page_size, search)


__all__ = [
    "SLIDER_ACTIVE_KEY",
    "SLIDER_ALL_KEY",
    "SLIDER_ALL_PATTERN",
    "SLIDER_BY_ID_KEY",
    "SLIDER_TRASHED_KEY",
    "TTL_DEFAULT",
    "slider_active_key",
    "slider_all_key",
    "slider_by_id_key",
    "slider_trashed_key",
]
