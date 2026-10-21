"""Merchant cache keys and TTL."""

from __future__ import annotations

MERCHANT_ALL_KEY = "merchant:all:page:%d:pageSize:%d:search:%s"
MERCHANT_BY_ID_KEY = "merchant:id:%d"
MERCHANT_ACTIVE_KEY = "merchant:active:page:%d:pageSize:%d:search:%s"
MERCHANT_TRASHED_KEY = "merchant:trashed:page:%d:pageSize:%d:search:%s"

MERCHANT_DOCUMENT_ALL_KEY = "merchant_document:all:page:%d:pageSize:%d:search:%s"
MERCHANT_DOCUMENT_BY_ID_KEY = "merchant_document:id:%d"
MERCHANT_DOCUMENT_ACTIVE_KEY = "merchant_document:active:page:%d:pageSize:%d:search:%s"
MERCHANT_DOCUMENT_TRASHED_KEY = (
    "merchant_document:trashed:page:%d:pageSize:%d:search:%s"
)

TTL_DEFAULT = 300  # 5 minutes (`ttlDefault`)

# Namespace flushed by the merchant command cache.
MERCHANT_ALL_PATTERN = "merchant:*"


def merchant_all_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_ALL_KEY % (page, page_size, search)


def merchant_by_id_key(merchant_id: int) -> str:
    return MERCHANT_BY_ID_KEY % merchant_id


def merchant_active_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_ACTIVE_KEY % (page, page_size, search)


def merchant_trashed_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_TRASHED_KEY % (page, page_size, search)


def merchant_document_all_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_DOCUMENT_ALL_KEY % (page, page_size, search)


def merchant_document_by_id_key(document_id: int) -> str:
    return MERCHANT_DOCUMENT_BY_ID_KEY % document_id


def merchant_document_active_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_DOCUMENT_ACTIVE_KEY % (page, page_size, search)


def merchant_document_trashed_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_DOCUMENT_TRASHED_KEY % (page, page_size, search)


__all__ = [
    "MERCHANT_ACTIVE_KEY",
    "MERCHANT_ALL_KEY",
    "MERCHANT_ALL_PATTERN",
    "MERCHANT_BY_ID_KEY",
    "MERCHANT_DOCUMENT_ACTIVE_KEY",
    "MERCHANT_DOCUMENT_ALL_KEY",
    "MERCHANT_DOCUMENT_BY_ID_KEY",
    "MERCHANT_DOCUMENT_TRASHED_KEY",
    "MERCHANT_TRASHED_KEY",
    "TTL_DEFAULT",
    "merchant_active_key",
    "merchant_all_key",
    "merchant_by_id_key",
    "merchant_document_active_key",
    "merchant_document_all_key",
    "merchant_document_by_id_key",
    "merchant_document_trashed_key",
    "merchant_trashed_key",
]
