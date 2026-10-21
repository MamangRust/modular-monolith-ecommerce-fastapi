"""merchant_business handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_business.handler.merchant_business_command import (
    MerchantBusinessCommandHandler,
)
from service.merchant_business.handler.merchant_business_query import (
    MerchantBusinessQueryHandler,
)
from service.merchant_business.service.service import Service


@dataclass(frozen=True)
class Handler:
    merchant_business_query: MerchantBusinessQueryHandler
    merchant_business_command: MerchantBusinessCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        merchant_business_query=MerchantBusinessQueryHandler(
            service.merchant_business_query, logger
        ),
        merchant_business_command=MerchantBusinessCommandHandler(
            service.merchant_business_command, logger
        ),
    )


__all__ = ["Handler", "new_handler"]
