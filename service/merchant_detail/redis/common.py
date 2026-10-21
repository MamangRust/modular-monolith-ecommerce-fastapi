"""merchant_detail cache keys and TTL."""

from __future__ import annotations

MERCHANT_DETAIL_ALL_KEY = "merchant_detail:all:page:%d:pageSize:%d:search:%s"
MERCHANT_DETAIL_BY_ID_KEY = "merchant_detail:id:%d"
MERCHANT_DETAIL_ACTIVE_KEY = "merchant_detail:active:page:%d:pageSize:%d:search:%s"
MERCHANT_DETAIL_TRASHED_KEY = (
    "merchant_detail:trashed:page:%d:pageSize:%d:search:%s"
)

TTL_DEFAULT = 300  # 5 minutes (`ttlDefault`)


def merchant_detail_all_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_DETAIL_ALL_KEY % (page, page_size, search)


def merchant_detail_by_id_key(merchant_detail_id: int) -> str:
    return MERCHANT_DETAIL_BY_ID_KEY % merchant_detail_id


def merchant_detail_active_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_DETAIL_ACTIVE_KEY % (page, page_size, search)


def merchant_detail_trashed_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_DETAIL_TRASHED_KEY % (page, page_size, search)


__all__ = [
    "MERCHANT_DETAIL_ACTIVE_KEY",
    "MERCHANT_DETAIL_ALL_KEY",
    "MERCHANT_DETAIL_BY_ID_KEY",
    "MERCHANT_DETAIL_TRASHED_KEY",
    "TTL_DEFAULT",
    "merchant_detail_active_key",
    "merchant_detail_all_key",
    "merchant_detail_by_id_key",
    "merchant_detail_trashed_key",
]
