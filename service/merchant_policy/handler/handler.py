"""merchant_policy handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_policy.handler.merchant_policy_command import (
    MerchantPolicyCommandHandler,
)
from service.merchant_policy.handler.merchant_policy_query import (
    MerchantPolicyQueryHandler,
)
from service.merchant_policy.service.service import Service


@dataclass(frozen=True)
class Handler:
    merchant_policy_query: MerchantPolicyQueryHandler
    merchant_policy_command: MerchantPolicyCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        merchant_policy_query=MerchantPolicyQueryHandler(
            service.merchant_policy_query, logger
        ),
        merchant_policy_command=MerchantPolicyCommandHandler(
            service.merchant_policy_command, logger
        ),
    )


__all__ = ["Handler", "new_handler"]
