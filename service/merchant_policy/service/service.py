"""merchant_policy service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_policy.redis import Mencache
from service.merchant_policy.repository.repository import Repositories
from service.merchant_policy.service.interfaces import (
    MerchantPolicyCommandService,
    MerchantPolicyQueryService,
)
from service.merchant_policy.service.merchant_policy_command_service import (
    MerchantPolicyCommandServiceImpl,
)
from service.merchant_policy.service.merchant_policy_query_service import (
    MerchantPolicyQueryServiceImpl,
)
from shared.observability import Observability

SERVICE_NAME = "merchant_policy-service"


@dataclass(frozen=True)
class Service:
    merchant_policy_query: MerchantPolicyQueryService
    merchant_policy_command: MerchantPolicyCommandService


def new_service(
    repos: Repositories,
    mencache: Mencache,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        merchant_policy_query=MerchantPolicyQueryServiceImpl(
            repos.merchant_policy_query,
            mencache.merchant_policy_query,
            logger,
            obs,
        ),
        merchant_policy_command=MerchantPolicyCommandServiceImpl(
            repos.merchant_policy_command,
            mencache.merchant_policy_command,
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]
