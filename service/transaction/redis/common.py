"""transaction cache keys and TTL. TTL is 5 minutes (`ttlDefault`). All transaction keys share the `transaction:` prefix, so the command cache's `InvalidateTransactionCache("transaction:*")` matches every written key. Note monthly stats keys put **month first, year second** in the label (`...:month:%d:year:%d`) while the setter passes `(month, year)` — kept as-is."""

from __future__ import annotations

TRANSACTION_ALL_KEY = "transaction:all:page:%d:pageSize:%d:search:%s"
TRANSACTION_BY_ID_KEY = "transaction:id:%d"
TRANSACTION_BY_MERCHANT_KEY = "transaction:merchant:%d:page:%d:pageSize:%d:search:%s"
TRANSACTION_ACTIVE_KEY = "transaction:active:page:%d:pageSize:%d:search:%s"
TRANSACTION_TRASHED_KEY = "transaction:trashed:page:%d:pageSize:%d:search:%s"
TRANSACTION_BY_ORDER_KEY = "transaction:order:%d"

TRANSACTION_MONTHLY_AMOUNT_SUCCESS_KEY = "transaction:month:amount:success:month:%d:year:%d"
TRANSACTION_MONTHLY_AMOUNT_FAILED_KEY = "transaction:month:amount:failed:month:%d:year:%d"
TRANSACTION_YEARLY_AMOUNT_SUCCESS_KEY = "transaction:year:amount:success:year:%d"
TRANSACTION_YEARLY_AMOUNT_FAILED_KEY = "transaction:year:amount:failed:year:%d"
TRANSACTION_MONTHLY_METHOD_SUCCESS_KEY = "transaction:month:method:success:month:%d:year:%d"
TRANSACTION_MONTHLY_METHOD_FAILED_KEY = "transaction:month:method:failed:month:%d:year:%d"
TRANSACTION_YEARLY_METHOD_SUCCESS_KEY = "transaction:year:method:success:year:%d"
TRANSACTION_YEARLY_METHOD_FAILED_KEY = "transaction:year:method:failed:year:%d"

TRANSACTION_MONTHLY_AMOUNT_SUCCESS_BY_MERCHANT_KEY = (
    "transaction:month:amount:success:merchant:%d:month:%d:year:%d"
)
TRANSACTION_MONTHLY_AMOUNT_FAILED_BY_MERCHANT_KEY = (
    "transaction:month:amount:failed:merchant:%d:month:%d:year:%d"
)
TRANSACTION_YEARLY_AMOUNT_SUCCESS_BY_MERCHANT_KEY = (
    "transaction:year:amount:success:merchant:%d:year:%d"
)
TRANSACTION_YEARLY_AMOUNT_FAILED_BY_MERCHANT_KEY = (
    "transaction:year:amount:failed:merchant:%d:year:%d"
)
TRANSACTION_MONTHLY_METHOD_SUCCESS_BY_MERCHANT_KEY = (
    "transaction:month:method:success:merchant:%d:month:%d:year:%d"
)
TRANSACTION_MONTHLY_METHOD_FAILED_BY_MERCHANT_KEY = (
    "transaction:month:method:failed:merchant:%d:month:%d:year:%d"
)
TRANSACTION_YEARLY_METHOD_SUCCESS_BY_MERCHANT_KEY = (
    "transaction:year:method:success:merchant:%d:year:%d"
)
TRANSACTION_YEARLY_METHOD_FAILED_BY_MERCHANT_KEY = (
    "transaction:year:method:failed:merchant:%d:year:%d"
)

TRANSACTION_NAMESPACE_PATTERN = "transaction:*"

TTL_DEFAULT = 300  # 5 minutes (`ttlDefault`)


def transaction_all_key(page: int, page_size: int, search: str) -> str:
    return TRANSACTION_ALL_KEY % (page, page_size, search)


def transaction_by_id_key(transaction_id: int) -> str:
    return TRANSACTION_BY_ID_KEY % transaction_id


def transaction_by_merchant_key(
    merchant_id: int, page: int, page_size: int, search: str
) -> str:
    return TRANSACTION_BY_MERCHANT_KEY % (merchant_id, page, page_size, search)


def transaction_active_key(page: int, page_size: int, search: str) -> str:
    return TRANSACTION_ACTIVE_KEY % (page, page_size, search)


def transaction_trashed_key(page: int, page_size: int, search: str) -> str:
    return TRANSACTION_TRASHED_KEY % (page, page_size, search)


def transaction_by_order_key(order_id: int) -> str:
    return TRANSACTION_BY_ORDER_KEY % order_id


__all__ = [
    "TTL_DEFAULT",
    "TRANSACTION_ACTIVE_KEY",
    "TRANSACTION_ALL_KEY",
    "TRANSACTION_BY_ID_KEY",
    "TRANSACTION_BY_MERCHANT_KEY",
    "TRANSACTION_BY_ORDER_KEY",
    "TRANSACTION_NAMESPACE_PATTERN",
    "TRANSACTION_TRASHED_KEY",
    "TRANSACTION_MONTHLY_AMOUNT_FAILED_BY_MERCHANT_KEY",
    "TRANSACTION_MONTHLY_AMOUNT_FAILED_KEY",
    "TRANSACTION_MONTHLY_AMOUNT_SUCCESS_BY_MERCHANT_KEY",
    "TRANSACTION_MONTHLY_AMOUNT_SUCCESS_KEY",
    "TRANSACTION_MONTHLY_METHOD_FAILED_BY_MERCHANT_KEY",
    "TRANSACTION_MONTHLY_METHOD_FAILED_KEY",
    "TRANSACTION_MONTHLY_METHOD_SUCCESS_BY_MERCHANT_KEY",
    "TRANSACTION_MONTHLY_METHOD_SUCCESS_KEY",
    "TRANSACTION_YEARLY_AMOUNT_FAILED_BY_MERCHANT_KEY",
    "TRANSACTION_YEARLY_AMOUNT_FAILED_KEY",
    "TRANSACTION_YEARLY_AMOUNT_SUCCESS_BY_MERCHANT_KEY",
    "TRANSACTION_YEARLY_AMOUNT_SUCCESS_KEY",
    "TRANSACTION_YEARLY_METHOD_FAILED_BY_MERCHANT_KEY",
    "TRANSACTION_YEARLY_METHOD_FAILED_KEY",
    "TRANSACTION_YEARLY_METHOD_SUCCESS_BY_MERCHANT_KEY",
    "TRANSACTION_YEARLY_METHOD_SUCCESS_KEY",
    "transaction_active_key",
    "transaction_all_key",
    "transaction_by_id_key",
    "transaction_by_merchant_key",
    "transaction_by_order_key",
    "transaction_trashed_key",
]
