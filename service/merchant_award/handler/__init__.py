"""merchant_award handler layer."""

from __future__ import annotations

from service.merchant_award.handler.handler import Handler, new_handler
from service.merchant_award.handler.merchant_award_command import (
    MerchantAwardCommandHandler,
)
from service.merchant_award.handler.merchant_award_query import (
    MerchantAwardQueryHandler,
)

__all__ = [
    "Handler",
    "MerchantAwardCommandHandler",
    "MerchantAwardQueryHandler",
    "new_handler",
]
