"""merchant_policy cache keys and TTL."""

from __future__ import annotations

MERCHANT_POLICY_ALL_KEY = "merchant_policy:all:page:%d:pageSize:%d:search:%s"
MERCHANT_POLICY_BY_ID_KEY = "merchant_policy:id:%d"
MERCHANT_POLICY_ACTIVE_KEY = "merchant_policy:active:page:%d:pageSize:%d:search:%s"
MERCHANT_POLICY_TRASHED_KEY = "merchant_policy:trashed:page:%d:pageSize:%d:search:%s"

TTL_DEFAULT = 300  # 5 minutes (`ttlDefault`)


def merchant_policy_all_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_POLICY_ALL_KEY % (page, page_size, search)


def merchant_policy_by_id_key(merchant_policy_id: int) -> str:
    return MERCHANT_POLICY_BY_ID_KEY % merchant_policy_id


def merchant_policy_active_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_POLICY_ACTIVE_KEY % (page, page_size, search)


def merchant_policy_trashed_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_POLICY_TRASHED_KEY % (page, page_size, search)


__all__ = [
    "MERCHANT_POLICY_ACTIVE_KEY",
    "MERCHANT_POLICY_ALL_KEY",
    "MERCHANT_POLICY_BY_ID_KEY",
    "MERCHANT_POLICY_TRASHED_KEY",
    "TTL_DEFAULT",
    "merchant_policy_active_key",
    "merchant_policy_all_key",
    "merchant_policy_by_id_key",
    "merchant_policy_trashed_key",
]
