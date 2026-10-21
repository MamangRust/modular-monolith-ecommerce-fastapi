"""order cache keys and TTL. TTL is 5 minutes (`ttlDefault`). All order keys share the `order:` prefix, so the command cache's `InvalidateCache("order:*")` matches every written key (no review-style normalisation needed)."""

from __future__ import annotations

ORDER_ALL_KEY = "order:all:page:%d:pageSize:%d:search:%s"
ORDER_BY_ID_KEY = "order:id:%d"
ORDER_ACTIVE_KEY = "order:active:page:%d:pageSize:%d:search:%s"
ORDER_TRASHED_KEY = "order:trashed:page:%d:pageSize:%d:search:%s"
ORDER_BY_MERCHANT_KEY = "order:merchant:merchantID:%d:page:%d:pageSize:%d:search:%s"

ORDER_MONTHLY_TOTAL_REVENUE_KEY = "order:monthly:totalRevenue:month:%d:year:%d"
ORDER_YEARLY_TOTAL_REVENUE_KEY = "order:yearly:totalRevenue:year:%d"
ORDER_MONTHLY_ORDER_KEY = "order:monthly:order:month:%d"
ORDER_YEARLY_ORDER_KEY = "order:yearly:order:year:%d"

ORDER_MONTHLY_TOTAL_REVENUE_BY_MERCHANT_KEY = (
    "order:monthly:totalRevenue:merchant:%d:month:%d:year:%d"
)
ORDER_YEARLY_TOTAL_REVENUE_BY_MERCHANT_KEY = (
    "order:yearly:totalRevenue:merchant:%d:year:%d"
)
ORDER_MONTHLY_ORDER_BY_MERCHANT_KEY = "order:monthly:order:merchant:%d:year:%d"
ORDER_YEARLY_ORDER_BY_MERCHANT_KEY = "order:yearly:order:merchant:%d:year:%d"

ORDER_NAMESPACE_PATTERN = "order:*"

TTL_DEFAULT = 300  # 5 minutes (`ttlDefault`)


def order_all_key(page: int, page_size: int, search: str) -> str:
    return ORDER_ALL_KEY % (page, page_size, search)


def order_by_id_key(order_id: int) -> str:
    return ORDER_BY_ID_KEY % order_id


def order_active_key(page: int, page_size: int, search: str) -> str:
    return ORDER_ACTIVE_KEY % (page, page_size, search)


def order_trashed_key(page: int, page_size: int, search: str) -> str:
    return ORDER_TRASHED_KEY % (page, page_size, search)


def order_by_merchant_key(
    merchant_id: int, page: int, page_size: int, search: str
) -> str:
    return ORDER_BY_MERCHANT_KEY % (merchant_id, page, page_size, search)


def order_monthly_total_revenue_key(month: int, year: int) -> str:
    return ORDER_MONTHLY_TOTAL_REVENUE_KEY % (month, year)


def order_yearly_total_revenue_key(year: int) -> str:
    return ORDER_YEARLY_TOTAL_REVENUE_KEY % year


def order_monthly_order_key(year: int) -> str:
    return ORDER_MONTHLY_ORDER_KEY % year


def order_yearly_order_key(year: int) -> str:
    return ORDER_YEARLY_ORDER_KEY % year


def order_monthly_total_revenue_by_merchant_key(
    merchant_id: int, month: int, year: int
) -> str:
    return ORDER_MONTHLY_TOTAL_REVENUE_BY_MERCHANT_KEY % (merchant_id, month, year)


def order_yearly_total_revenue_by_merchant_key(merchant_id: int, year: int) -> str:
    return ORDER_YEARLY_TOTAL_REVENUE_BY_MERCHANT_KEY % (merchant_id, year)


def order_monthly_order_by_merchant_key(merchant_id: int, year: int) -> str:
    return ORDER_MONTHLY_ORDER_BY_MERCHANT_KEY % (merchant_id, year)


def order_yearly_order_by_merchant_key(merchant_id: int, year: int) -> str:
    return ORDER_YEARLY_ORDER_BY_MERCHANT_KEY % (merchant_id, year)


__all__ = [
    "ORDER_ACTIVE_KEY",
    "ORDER_ALL_KEY",
    "ORDER_BY_ID_KEY",
    "ORDER_BY_MERCHANT_KEY",
    "ORDER_MONTHLY_ORDER_BY_MERCHANT_KEY",
    "ORDER_MONTHLY_ORDER_KEY",
    "ORDER_MONTHLY_TOTAL_REVENUE_BY_MERCHANT_KEY",
    "ORDER_MONTHLY_TOTAL_REVENUE_KEY",
    "ORDER_NAMESPACE_PATTERN",
    "ORDER_TRASHED_KEY",
    "ORDER_YEARLY_ORDER_BY_MERCHANT_KEY",
    "ORDER_YEARLY_ORDER_KEY",
    "ORDER_YEARLY_TOTAL_REVENUE_BY_MERCHANT_KEY",
    "ORDER_YEARLY_TOTAL_REVENUE_KEY",
    "TTL_DEFAULT",
    "order_active_key",
    "order_all_key",
    "order_by_id_key",
    "order_by_merchant_key",
    "order_monthly_order_by_merchant_key",
    "order_monthly_order_key",
    "order_monthly_total_revenue_by_merchant_key",
    "order_monthly_total_revenue_key",
    "order_trashed_key",
    "order_yearly_order_by_merchant_key",
    "order_yearly_order_key",
    "order_yearly_total_revenue_by_merchant_key",
    "order_yearly_total_revenue_key",
]
