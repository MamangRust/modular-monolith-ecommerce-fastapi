"""merchant_business cache keys and TTL."""

from __future__ import annotations

MERCHANT_BUSINESS_ALL_KEY = "merchant_business:all:page:%d:pageSize:%d:search:%s"
MERCHANT_BUSINESS_BY_ID_KEY = "merchant_business:id:%d"
MERCHANT_BUSINESS_ACTIVE_KEY = (
    "merchant_business:active:page:%d:pageSize:%d:search:%s"
)
MERCHANT_BUSINESS_TRASHED_KEY = (
    "merchant_business:trashed:page:%d:pageSize:%d:search:%s"
)

TTL_DEFAULT = 300  # 5 minutes (`ttlDefault`)


def merchant_business_all_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_BUSINESS_ALL_KEY % (page, page_size, search)


def merchant_business_by_id_key(merchant_business_info_id: int) -> str:
    return MERCHANT_BUSINESS_BY_ID_KEY % merchant_business_info_id


def merchant_business_active_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_BUSINESS_ACTIVE_KEY % (page, page_size, search)


def merchant_business_trashed_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_BUSINESS_TRASHED_KEY % (page, page_size, search)


__all__ = [
    "MERCHANT_BUSINESS_ACTIVE_KEY",
    "MERCHANT_BUSINESS_ALL_KEY",
    "MERCHANT_BUSINESS_BY_ID_KEY",
    "MERCHANT_BUSINESS_TRASHED_KEY",
    "TTL_DEFAULT",
    "merchant_business_active_key",
    "merchant_business_all_key",
    "merchant_business_by_id_key",
    "merchant_business_trashed_key",
]
