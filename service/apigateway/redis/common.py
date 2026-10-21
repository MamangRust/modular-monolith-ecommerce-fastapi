"""Gateway cache keys and TTLs. Card keys are byte-identical to the card *domain* cache keys (`service/card/redis/common.py`) because the gateway duplicates the same constants in its own `api/card` package. They do not collide: the gateway uses its own Redis DB (`REDIS_DB` default 0) while the card service uses `REDIS_DB_CARD` (3). The gateway also caches whole REST envelopes here, whereas the domain caches row objects."""

from __future__ import annotations

USER_ROLES_KEY = "user_roles:%s"
USER_ROLES_TTL = 300  # 5 minutes, matching the role validator cache

# Gateway auth cache. Note these differ from the auth *service* cache keys
# (`identity:refresh_token:` / `identity:user_info:`): the gateway caches
# whole API responses under its own namespace. `auth:login:` is shared with
# the service key, but the service never writes it (it only uses the lockout
# counters), so there is no collision.
AUTH_LOGIN_KEY = "auth:login:%s"
AUTH_REFRESH_TOKEN_KEY = "auth:refresh_token:%s"
AUTH_USER_INFO_KEY = "auth:user_info:%s"
AUTH_TTL = 300  # 5 minutes

CARD_ALL_KEY = "card:all:page:%d:pageSize:%d:search:%s"
CARD_BY_ID_KEY = "card:id:%d"
CARD_ACTIVE_KEY = "card:active:page:%d:pageSize:%d:search:%s"
CARD_TRASHED_KEY = "card:trashed:page:%d:pageSize:%d:search:%s"
CARD_BY_USER_ID_KEY = "card:user_id:%d"
CARD_BY_CARD_NUMBER_KEY = "card:card_number:%s"
CARD_TTL = 300  # 5 minutes

# Keys are byte-identical to the saldo *domain* cache keys
# because the gateway duplicates the same constants in its own package.
SALDO_ALL_KEY = "saldo:all:page:%d:pageSize:%d:search:%s"
SALDO_ACTIVE_KEY = "saldo:active:page:%d:pageSize:%d:search:%s"
SALDO_TRASHED_KEY = "saldo:trashed:page:%d:pageSize:%d:search:%s"
SALDO_BY_ID_KEY = "saldo:id:%d"
SALDO_BY_CARD_NUMBER_KEY = "saldo:card_number:%s"
SALDO_MONTH_TOTAL_BALANCE_KEY = "saldo:month_total_balance:month:%d:year:%d"
SALDO_YEAR_TOTAL_BALANCE_KEY = "saldo:year_total_balance:year:%d"
SALDO_YEARLY_BALANCE_KEY = "saldo:yearly_balance:year:%d"
SALDO_MONTH_BALANCE_KEY = "saldo:month_balance:year:%d"
SALDO_TTL = 300  # 5 minutes

# Gateway merchant response cache (`apigateway/redis/api/merchant/**`).
MERCHANT_ALL_KEY = "merchant:all:page:%d:pageSize:%d:search:%s"
MERCHANT_BY_ID_KEY = "merchant:id:%d"
MERCHANT_ACTIVE_KEY = "merchant:active:page:%d:pageSize:%d:search:%s"
MERCHANT_TRASHED_KEY = "merchant:trashed:page:%d:pageSize:%d:search:%s"
MERCHANT_BY_API_KEY_KEY = "merchant:api_key:%s"
MERCHANT_BY_USER_ID_KEY = "merchant:user_id:%d"
MERCHANT_TRANSACTIONS_KEY = "merchant:transaction:search:%s:page:%d:pageSize:%d"
MERCHANT_TRANSACTION_APIKEY_KEY = (
    "merchant:transaction:apikey:%s:search:%s:page:%d:pageSize:%d"
)
MERCHANT_TRANSACTION_KEY = (
    "merchant:transaction:merchant:%d:search:%s:page:%d:pageSize:%d"
)
MERCHANT_MONTHLY_PAYMENT_METHOD_KEY = "merchant:statistic:monthly:payment-method:year:%d"
MERCHANT_YEARLY_PAYMENT_METHOD_KEY = "merchant:statistic:yearly:payment-method:year:%d"
MERCHANT_MONTHLY_AMOUNT_KEY = "merchant:statistic:monthly:amount:year:%d"
MERCHANT_YEARLY_AMOUNT_KEY = "merchant:statistic:yearly:amount:year:%d"
MERCHANT_MONTHLY_TOTAL_AMOUNT_KEY = "merchant:statistic:monthly:total-amount:year:%d"
MERCHANT_YEARLY_TOTAL_AMOUNT_KEY = "merchant:statistic:yearly:total-amount:year:%d"
MERCHANT_MONTHLY_PAYMENT_METHOD_BY_APIKEY_KEY = (
    "merchant:statistic:monthly:payment-method:apikey:%s:year:%d"
)
MERCHANT_YEARLY_PAYMENT_METHOD_BY_APIKEY_KEY = (
    "merchant:statistic:yearly:payment-method:apikey:%s:year:%d"
)
MERCHANT_MONTHLY_AMOUNT_BY_APIKEY_KEY = (
    "merchant:statistic:monthly:amount:apikey:%s:year:%d"
)
MERCHANT_YEARLY_AMOUNT_BY_APIKEY_KEY = (
    "merchant:statistic:yearly:amount:apikey:%s:year:%d"
)
MERCHANT_MONTHLY_TOTAL_AMOUNT_BY_APIKEY_KEY = (
    "merchant:statistic:monthly:total-amount:apikey:%s:year:%d"
)
MERCHANT_YEARLY_TOTAL_AMOUNT_BY_APIKEY_KEY = (
    "merchant:statistic:yearly:total-amount:apikey:%s:year:%d"
)
MERCHANT_MONTHLY_PAYMENT_METHOD_BY_MERCHANT_KEY = (
    "merchant:statistic:monthly:payment-method:merchant-id:%d:year:%d"
)
MERCHANT_YEARLY_PAYMENT_METHOD_BY_MERCHANT_KEY = (
    "merchant:statistic:yearly:payment-method:merchant-id:%d:year:%d"
)
MERCHANT_MONTHLY_AMOUNT_BY_MERCHANT_KEY = (
    "merchant:statistic:monthly:amount:merchant-id:%d:year:%d"
)
MERCHANT_YEARLY_AMOUNT_BY_MERCHANT_KEY = (
    "merchant:statistic:yearly:amount:merchant-id:%d:year:%d"
)
MERCHANT_MONTHLY_TOTAL_AMOUNT_BY_MERCHANT_KEY = (
    "merchant:statistic:monthly:total-amount:merchant-id:%d:year:%d"
)
MERCHANT_YEARLY_TOTAL_AMOUNT_BY_MERCHANT_KEY = (
    "merchant:statistic:yearly:total-amount:merchant-id:%d:year:%d"
)
MERCHANT_TTL = 300  # 5 minutes

# Gateway merchant-document response cache
# (`apigateway/redis/api/merchantdocument`).
MERCHANT_DOCUMENT_ALL_KEY = "merchant_document:all:page:%d:pageSize:%d:search:%s"
MERCHANT_DOCUMENT_BY_ID_KEY = "merchant_document:id:%d"
MERCHANT_DOCUMENT_ACTIVE_KEY = "merchant_document:active:page:%d:pageSize:%d:search:%s"
MERCHANT_DOCUMENT_TRASHED_KEY = "merchant_document:trashed:page:%d:pageSize:%d:search:%s"
MERCHANT_DOCUMENT_TTL = 300  # 5 minutes


def user_roles_key(user_id: int | str) -> str:
    return USER_ROLES_KEY % user_id


def auth_login_key(email: str) -> str:
    return AUTH_LOGIN_KEY % email


def auth_refresh_token_key(token: str) -> str:
    return AUTH_REFRESH_TOKEN_KEY % token


def auth_user_info_key(user_id: int | str) -> str:
    return AUTH_USER_INFO_KEY % user_id


def card_all_key(page: int, page_size: int, search: str) -> str:
    return CARD_ALL_KEY % (page, page_size, search)


def card_by_id_key(card_id: int) -> str:
    return CARD_BY_ID_KEY % card_id


def card_active_key(page: int, page_size: int, search: str) -> str:
    return CARD_ACTIVE_KEY % (page, page_size, search)


def card_trashed_key(page: int, page_size: int, search: str) -> str:
    return CARD_TRASHED_KEY % (page, page_size, search)


def card_by_user_id_key(user_id: int) -> str:
    return CARD_BY_USER_ID_KEY % user_id


def card_by_card_number_key(card_number: str) -> str:
    return CARD_BY_CARD_NUMBER_KEY % card_number


def saldo_all_key(page: int, page_size: int, search: str) -> str:
    return SALDO_ALL_KEY % (page, page_size, search)


def saldo_active_key(page: int, page_size: int, search: str) -> str:
    return SALDO_ACTIVE_KEY % (page, page_size, search)


def saldo_trashed_key(page: int, page_size: int, search: str) -> str:
    return SALDO_TRASHED_KEY % (page, page_size, search)


def saldo_by_id_key(saldo_id: int) -> str:
    return SALDO_BY_ID_KEY % saldo_id


def saldo_by_card_number_key(card_number: str) -> str:
    return SALDO_BY_CARD_NUMBER_KEY % card_number


def saldo_month_total_balance_key(month: int, year: int) -> str:
    return SALDO_MONTH_TOTAL_BALANCE_KEY % (month, year)


def saldo_year_total_balance_key(year: int) -> str:
    return SALDO_YEAR_TOTAL_BALANCE_KEY % year


def saldo_yearly_balance_key(year: int) -> str:
    return SALDO_YEARLY_BALANCE_KEY % year


def saldo_month_balance_key(year: int) -> str:
    return SALDO_MONTH_BALANCE_KEY % year


def merchant_all_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_ALL_KEY % (page, page_size, search)


def merchant_by_id_key(merchant_id: int) -> str:
    return MERCHANT_BY_ID_KEY % merchant_id


def merchant_active_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_ACTIVE_KEY % (page, page_size, search)


def merchant_trashed_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_TRASHED_KEY % (page, page_size, search)


def merchant_by_api_key_key(api_key: str) -> str:
    return MERCHANT_BY_API_KEY_KEY % api_key


def merchant_by_user_id_key(user_id: int) -> str:
    return MERCHANT_BY_USER_ID_KEY % user_id


def merchant_transactions_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_TRANSACTIONS_KEY % (search, page, page_size)


def merchant_transaction_apikey_key(
    api_key: str, page: int, page_size: int, search: str
) -> str:
    return MERCHANT_TRANSACTION_APIKEY_KEY % (api_key, search, page, page_size)


def merchant_transaction_key(
    merchant_id: int, page: int, page_size: int, search: str
) -> str:
    return MERCHANT_TRANSACTION_KEY % (merchant_id, search, page, page_size)


def merchant_monthly_payment_method_key(year: int) -> str:
    return MERCHANT_MONTHLY_PAYMENT_METHOD_KEY % year


def merchant_yearly_payment_method_key(year: int) -> str:
    return MERCHANT_YEARLY_PAYMENT_METHOD_KEY % year


def merchant_monthly_amount_key(year: int) -> str:
    return MERCHANT_MONTHLY_AMOUNT_KEY % year


def merchant_yearly_amount_key(year: int) -> str:
    return MERCHANT_YEARLY_AMOUNT_KEY % year


def merchant_monthly_total_amount_key(year: int) -> str:
    return MERCHANT_MONTHLY_TOTAL_AMOUNT_KEY % year


def merchant_yearly_total_amount_key(year: int) -> str:
    return MERCHANT_YEARLY_TOTAL_AMOUNT_KEY % year


def merchant_monthly_payment_method_by_apikey_key(api_key: str, year: int) -> str:
    return MERCHANT_MONTHLY_PAYMENT_METHOD_BY_APIKEY_KEY % (api_key, year)


def merchant_yearly_payment_method_by_apikey_key(api_key: str, year: int) -> str:
    return MERCHANT_YEARLY_PAYMENT_METHOD_BY_APIKEY_KEY % (api_key, year)


def merchant_monthly_amount_by_apikey_key(api_key: str, year: int) -> str:
    return MERCHANT_MONTHLY_AMOUNT_BY_APIKEY_KEY % (api_key, year)


def merchant_yearly_amount_by_apikey_key(api_key: str, year: int) -> str:
    return MERCHANT_YEARLY_AMOUNT_BY_APIKEY_KEY % (api_key, year)


def merchant_monthly_total_amount_by_apikey_key(api_key: str, year: int) -> str:
    return MERCHANT_MONTHLY_TOTAL_AMOUNT_BY_APIKEY_KEY % (api_key, year)


def merchant_yearly_total_amount_by_apikey_key(api_key: str, year: int) -> str:
    return MERCHANT_YEARLY_TOTAL_AMOUNT_BY_APIKEY_KEY % (api_key, year)


def merchant_monthly_payment_method_by_merchant_key(
    merchant_id: int, year: int
) -> str:
    return MERCHANT_MONTHLY_PAYMENT_METHOD_BY_MERCHANT_KEY % (merchant_id, year)


def merchant_yearly_payment_method_by_merchant_key(merchant_id: int, year: int) -> str:
    return MERCHANT_YEARLY_PAYMENT_METHOD_BY_MERCHANT_KEY % (merchant_id, year)


def merchant_monthly_amount_by_merchant_key(merchant_id: int, year: int) -> str:
    return MERCHANT_MONTHLY_AMOUNT_BY_MERCHANT_KEY % (merchant_id, year)


def merchant_yearly_amount_by_merchant_key(merchant_id: int, year: int) -> str:
    return MERCHANT_YEARLY_AMOUNT_BY_MERCHANT_KEY % (merchant_id, year)


def merchant_monthly_total_amount_by_merchant_key(merchant_id: int, year: int) -> str:
    return MERCHANT_MONTHLY_TOTAL_AMOUNT_BY_MERCHANT_KEY % (merchant_id, year)


def merchant_yearly_total_amount_by_merchant_key(merchant_id: int, year: int) -> str:
    return MERCHANT_YEARLY_TOTAL_AMOUNT_BY_MERCHANT_KEY % (merchant_id, year)


def merchant_document_all_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_DOCUMENT_ALL_KEY % (page, page_size, search)


def merchant_document_by_id_key(document_id: int) -> str:
    return MERCHANT_DOCUMENT_BY_ID_KEY % document_id


def merchant_document_active_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_DOCUMENT_ACTIVE_KEY % (page, page_size, search)


def merchant_document_trashed_key(page: int, page_size: int, search: str) -> str:
    return MERCHANT_DOCUMENT_TRASHED_KEY % (page, page_size, search)


__all__ = [
    "AUTH_LOGIN_KEY",
    "AUTH_REFRESH_TOKEN_KEY",
    "AUTH_TTL",
    "AUTH_USER_INFO_KEY",
    "CARD_ACTIVE_KEY",
    "CARD_ALL_KEY",
    "CARD_BY_CARD_NUMBER_KEY",
    "CARD_BY_ID_KEY",
    "CARD_BY_USER_ID_KEY",
    "CARD_TRASHED_KEY",
    "CARD_TTL",
    "USER_ROLES_KEY",
    "USER_ROLES_TTL",
    "auth_login_key",
    "auth_refresh_token_key",
    "auth_user_info_key",
    "card_active_key",
    "card_all_key",
    "card_by_card_number_key",
    "card_by_id_key",
    "card_by_user_id_key",
    "card_trashed_key",
    "SALDO_ACTIVE_KEY",
    "SALDO_ALL_KEY",
    "SALDO_BY_CARD_NUMBER_KEY",
    "SALDO_BY_ID_KEY",
    "SALDO_MONTH_BALANCE_KEY",
    "SALDO_MONTH_TOTAL_BALANCE_KEY",
    "SALDO_TRASHED_KEY",
    "SALDO_TTL",
    "SALDO_YEARLY_BALANCE_KEY",
    "SALDO_YEAR_TOTAL_BALANCE_KEY",
    "saldo_active_key",
    "saldo_all_key",
    "saldo_by_card_number_key",
    "saldo_by_id_key",
    "saldo_month_balance_key",
    "saldo_month_total_balance_key",
    "saldo_trashed_key",
    "saldo_yearly_balance_key",
    "saldo_year_total_balance_key",
    "user_roles_key",
    "MERCHANT_ACTIVE_KEY",
    "MERCHANT_ALL_KEY",
    "MERCHANT_BY_API_KEY_KEY",
    "MERCHANT_BY_ID_KEY",
    "MERCHANT_BY_USER_ID_KEY",
    "MERCHANT_DOCUMENT_ACTIVE_KEY",
    "MERCHANT_DOCUMENT_ALL_KEY",
    "MERCHANT_DOCUMENT_BY_ID_KEY",
    "MERCHANT_DOCUMENT_TRASHED_KEY",
    "MERCHANT_DOCUMENT_TTL",
    "MERCHANT_MONTHLY_AMOUNT_BY_APIKEY_KEY",
    "MERCHANT_MONTHLY_AMOUNT_BY_MERCHANT_KEY",
    "MERCHANT_MONTHLY_AMOUNT_KEY",
    "MERCHANT_MONTHLY_PAYMENT_METHOD_BY_APIKEY_KEY",
    "MERCHANT_MONTHLY_PAYMENT_METHOD_BY_MERCHANT_KEY",
    "MERCHANT_MONTHLY_PAYMENT_METHOD_KEY",
    "MERCHANT_MONTHLY_TOTAL_AMOUNT_BY_APIKEY_KEY",
    "MERCHANT_MONTHLY_TOTAL_AMOUNT_BY_MERCHANT_KEY",
    "MERCHANT_MONTHLY_TOTAL_AMOUNT_KEY",
    "MERCHANT_TRANSACTION_APIKEY_KEY",
    "MERCHANT_TRANSACTIONS_KEY",
    "MERCHANT_TRANSACTION_KEY",
    "MERCHANT_TRASHED_KEY",
    "MERCHANT_TTL",
    "MERCHANT_YEARLY_AMOUNT_BY_APIKEY_KEY",
    "MERCHANT_YEARLY_AMOUNT_BY_MERCHANT_KEY",
    "MERCHANT_YEARLY_AMOUNT_KEY",
    "MERCHANT_YEARLY_PAYMENT_METHOD_BY_APIKEY_KEY",
    "MERCHANT_YEARLY_PAYMENT_METHOD_BY_MERCHANT_KEY",
    "MERCHANT_YEARLY_PAYMENT_METHOD_KEY",
    "MERCHANT_YEARLY_TOTAL_AMOUNT_BY_APIKEY_KEY",
    "MERCHANT_YEARLY_TOTAL_AMOUNT_BY_MERCHANT_KEY",
    "MERCHANT_YEARLY_TOTAL_AMOUNT_KEY",
    "merchant_active_key",
    "merchant_all_key",
    "merchant_by_api_key_key",
    "merchant_by_id_key",
    "merchant_by_user_id_key",
    "merchant_document_active_key",
    "merchant_document_all_key",
    "merchant_document_by_id_key",
    "merchant_document_trashed_key",
    "merchant_monthly_amount_by_apikey_key",
    "merchant_monthly_amount_by_merchant_key",
    "merchant_monthly_amount_key",
    "merchant_monthly_payment_method_by_apikey_key",
    "merchant_monthly_payment_method_by_merchant_key",
    "merchant_monthly_payment_method_key",
    "merchant_monthly_total_amount_by_apikey_key",
    "merchant_monthly_total_amount_by_merchant_key",
    "merchant_monthly_total_amount_key",
    "merchant_transaction_apikey_key",
    "merchant_transaction_key",
    "merchant_transactions_key",
    "merchant_trashed_key",
    "merchant_yearly_amount_by_apikey_key",
    "merchant_yearly_amount_by_merchant_key",
    "merchant_yearly_amount_key",
    "merchant_yearly_payment_method_by_apikey_key",
    "merchant_yearly_payment_method_by_merchant_key",
    "merchant_yearly_payment_method_key",
    "merchant_yearly_total_amount_by_apikey_key",
    "merchant_yearly_total_amount_by_merchant_key",
    "merchant_yearly_total_amount_key",
]
