"""Category cache keys and TTL."""

from __future__ import annotations

TTL_DEFAULT = 300  # 5 minutes

# ---- query keys ----
CATEGORY_ALL_KEY = "category:all:page:%d:pageSize:%d:search:%s"
CATEGORY_BY_ID_KEY = "category:id:%d"
CATEGORY_ACTIVE_KEY = "category:active:page:%d:pageSize:%d:search:%s"
CATEGORY_TRASHED_KEY = "category:trashed:page:%d:pageSize:%d:search:%s"

# ---- stats keys (base) ----
CATEGORY_STATS_MONTH_TOTAL_PRICE_KEY = "category:stats:month:%d:year:%d"
CATEGORY_STATS_YEAR_TOTAL_PRICE_KEY = "category:stats:year-total:%d"
CATEGORY_STATS_MONTH_PRICE_KEY = "category:stats:month:%d"
CATEGORY_STATS_YEAR_PRICE_KEY = "category:stats:year-price:%d"

# ---- stats keys (by id) ----
CATEGORY_STATS_BYID_MONTH_TOTAL_PRICE_KEY = "category:stats:byid:%d:month:%d:year:%d"
CATEGORY_STATS_BYID_YEAR_TOTAL_PRICE_KEY = "category:stats:byid:%d:year-total:%d"
CATEGORY_STATS_BYID_MONTH_PRICE_KEY = "category:stats:byid:%d:month:%d"
CATEGORY_STATS_BYID_YEAR_PRICE_KEY = "category:stats:byid:%d:year-price:%d"

# ---- stats keys (by merchant) ----
CATEGORY_STATS_BYMERCHANT_MONTH_TOTAL_PRICE_KEY = (
    "category:stats:bymerchant:%d:month:%d:year:%d"
)
CATEGORY_STATS_BYMERCHANT_YEAR_TOTAL_PRICE_KEY = (
    "category:stats:bymerchant:%d:year-total:%d"
)
CATEGORY_STATS_BYMERCHANT_MONTH_PRICE_KEY = "category:stats:bymerchant:%d:month:%d"
CATEGORY_STATS_BYMERCHANT_YEAR_PRICE_KEY = "category:stats:bymerchant:%d:year-price:%d"

# Patterns cleared after a category mutation. only dropped
# `category:id:<id>` and never invalidated lists; both
# (see CategoryCommandCacheImpl).
LIST_PATTERNS = (
    "category:all:page:*",
    "category:active:page:*",
    "category:trashed:page:*",
)


def category_all_key(page: int, page_size: int, search: str) -> str:
    return CATEGORY_ALL_KEY % (page, page_size, search)


def category_by_id_key(category_id: int) -> str:
    return CATEGORY_BY_ID_KEY % category_id


def category_active_key(page: int, page_size: int, search: str) -> str:
    return CATEGORY_ACTIVE_KEY % (page, page_size, search)


def category_trashed_key(page: int, page_size: int, search: str) -> str:
    return CATEGORY_TRASHED_KEY % (page, page_size, search)


def stats_month_total_price_key(month: int, year: int) -> str:
    return CATEGORY_STATS_MONTH_TOTAL_PRICE_KEY % (month, year)


def stats_year_total_price_key(year: int) -> str:
    return CATEGORY_STATS_YEAR_TOTAL_PRICE_KEY % year


def stats_month_price_key(year: int) -> str:
    return CATEGORY_STATS_MONTH_PRICE_KEY % year


def stats_year_price_key(year: int) -> str:
    return CATEGORY_STATS_YEAR_PRICE_KEY % year


def stats_byid_month_total_price_key(category_id: int, month: int, year: int) -> str:
    return CATEGORY_STATS_BYID_MONTH_TOTAL_PRICE_KEY % (category_id, month, year)


def stats_byid_year_total_price_key(category_id: int, year: int) -> str:
    return CATEGORY_STATS_BYID_YEAR_TOTAL_PRICE_KEY % (category_id, year)


def stats_byid_month_price_key(category_id: int, year: int) -> str:
    return CATEGORY_STATS_BYID_MONTH_PRICE_KEY % (category_id, year)


def stats_byid_year_price_key(category_id: int, year: int) -> str:
    return CATEGORY_STATS_BYID_YEAR_PRICE_KEY % (category_id, year)


def stats_bymerchant_month_total_price_key(
    merchant_id: int, month: int, year: int
) -> str:
    return CATEGORY_STATS_BYMERCHANT_MONTH_TOTAL_PRICE_KEY % (
        merchant_id,
        month,
        year,
    )


def stats_bymerchant_year_total_price_key(merchant_id: int, year: int) -> str:
    return CATEGORY_STATS_BYMERCHANT_YEAR_TOTAL_PRICE_KEY % (merchant_id, year)


def stats_bymerchant_month_price_key(merchant_id: int, year: int) -> str:
    return CATEGORY_STATS_BYMERCHANT_MONTH_PRICE_KEY % (merchant_id, year)


def stats_bymerchant_year_price_key(merchant_id: int, year: int) -> str:
    return CATEGORY_STATS_BYMERCHANT_YEAR_PRICE_KEY % (merchant_id, year)


__all__ = [
    "CATEGORY_ACTIVE_KEY",
    "CATEGORY_ALL_KEY",
    "CATEGORY_BY_ID_KEY",
    "CATEGORY_STATS_BYID_MONTH_PRICE_KEY",
    "CATEGORY_STATS_BYID_MONTH_TOTAL_PRICE_KEY",
    "CATEGORY_STATS_BYID_YEAR_PRICE_KEY",
    "CATEGORY_STATS_BYID_YEAR_TOTAL_PRICE_KEY",
    "CATEGORY_STATS_BYMERCHANT_MONTH_PRICE_KEY",
    "CATEGORY_STATS_BYMERCHANT_MONTH_TOTAL_PRICE_KEY",
    "CATEGORY_STATS_BYMERCHANT_YEAR_PRICE_KEY",
    "CATEGORY_STATS_BYMERCHANT_YEAR_TOTAL_PRICE_KEY",
    "CATEGORY_STATS_MONTH_PRICE_KEY",
    "CATEGORY_STATS_MONTH_TOTAL_PRICE_KEY",
    "CATEGORY_STATS_YEAR_PRICE_KEY",
    "CATEGORY_STATS_YEAR_TOTAL_PRICE_KEY",
    "CATEGORY_TRASHED_KEY",
    "LIST_PATTERNS",
    "TTL_DEFAULT",
    "category_active_key",
    "category_all_key",
    "category_by_id_key",
    "category_trashed_key",
    "stats_byid_month_price_key",
    "stats_byid_month_total_price_key",
    "stats_byid_year_price_key",
    "stats_byid_year_total_price_key",
    "stats_bymerchant_month_price_key",
    "stats_bymerchant_month_total_price_key",
    "stats_bymerchant_year_price_key",
    "stats_bymerchant_year_total_price_key",
    "stats_month_price_key",
    "stats_month_total_price_key",
    "stats_year_price_key",
    "stats_year_total_price_key",
]
