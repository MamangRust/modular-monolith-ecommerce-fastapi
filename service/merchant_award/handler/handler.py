"""merchant_award handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_award.handler.merchant_award_command import (
    MerchantAwardCommandHandler,
)
from service.merchant_award.handler.merchant_award_query import (
    MerchantAwardQueryHandler,
)
from service.merchant_award.service.service import Service


@dataclass(frozen=True)
class Handler:
    merchant_award_query: MerchantAwardQueryHandler
    merchant_award_command: MerchantAwardCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        merchant_award_query=MerchantAwardQueryHandler(
            service.merchant_award_query, logger
        ),
        merchant_award_command=MerchantAwardCommandHandler(
            service.merchant_award_command, logger
        ),
    )


__all__ = ["Handler", "new_handler"]
