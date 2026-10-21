"""transaction service layer."""

from __future__ import annotations

from service.transaction.service.interfaces import (
    TransactionCommandService,
    TransactionQueryService,
    TransactionStatsByMerchantService,
    TransactionStatsService,
)
from service.transaction.service.payment_state_machine import (
    PAYMENT_STATUS_FAILED,
    PAYMENT_STATUS_PENDING,
    PAYMENT_STATUS_REFUNDED,
    PAYMENT_STATUS_SUCCESS,
    can_transition_payment_status,
    is_valid_payment_status,
    normalize_payment_status,
)
from service.transaction.service.service import SERVICE_NAME, Service, new_service
from service.transaction.service.transaction_command_service import (
    TransactionCommandServiceImpl,
)
from service.transaction.service.transaction_query_service import (
    TransactionQueryServiceImpl,
)
from service.transaction.service.transaction_stats_by_merchant_service import (
    TransactionStatsByMerchantServiceImpl,
)
from service.transaction.service.transaction_stats_service import (
    TransactionStatsServiceImpl,
)

__all__ = [
    "PAYMENT_STATUS_FAILED",
    "PAYMENT_STATUS_PENDING",
    "PAYMENT_STATUS_REFUNDED",
    "PAYMENT_STATUS_SUCCESS",
    "SERVICE_NAME",
    "Service",
    "TransactionCommandService",
    "TransactionCommandServiceImpl",
    "TransactionQueryService",
    "TransactionQueryServiceImpl",
    "TransactionStatsByMerchantService",
    "TransactionStatsByMerchantServiceImpl",
    "TransactionStatsService",
    "TransactionStatsServiceImpl",
    "can_transition_payment_status",
    "is_valid_payment_status",
    "new_service",
    "normalize_payment_status",
]
