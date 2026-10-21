"""merchant_award cache keys and TTL."""

from __future__ import annotations

MERCHANT_AWARD_ALL_KEY = "merchant_award:all:page:%d:pageSize:%d:search:%s"
MERCHANT_AWARD_BY_ID_KEY = "merchant_award:id:%d"
MERCHANT_AWARD_ACTIVE_KEY = "merchant_award:active:page:%d:pageSize:%d:search:%s"
MERCHANT_AWARD_TRASHED_KEY = "merchant_award:trashed:page:%d:pageSize:%d:search:%s"

TTL_DEFAULT = 300  # 5 minutes (`ttlDefault`)


def merchant_award_all_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_AWARD_ALL_KEY % (page, page_size, search)


def merchant_award_by_id_key(merchant_certification_id: int) -> str:
    return MERCHANT_AWARD_BY_ID_KEY % merchant_certification_id


def merchant_award_active_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_AWARD_ACTIVE_KEY % (page, page_size, search)


def merchant_award_trashed_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_AWARD_TRASHED_KEY % (page, page_size, search)


__all__ = [
    "MERCHANT_AWARD_ACTIVE_KEY",
    "MERCHANT_AWARD_ALL_KEY",
    "MERCHANT_AWARD_BY_ID_KEY",
    "MERCHANT_AWARD_TRASHED_KEY",
    "TTL_DEFAULT",
    "merchant_award_active_key",
    "merchant_award_all_key",
    "merchant_award_by_id_key",
    "merchant_award_trashed_key",
]
