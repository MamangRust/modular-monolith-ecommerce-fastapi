"""merchant_award service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_award.redis import Mencache
from service.merchant_award.repository.repository import Repositories
from service.merchant_award.service.interfaces import (
    MerchantAwardCommandService,
    MerchantAwardQueryService,
)
from service.merchant_award.service.merchant_award_command_service import (
    MerchantAwardCommandServiceImpl,
)
from service.merchant_award.service.merchant_award_query_service import (
    MerchantAwardQueryServiceImpl,
)
from shared.observability import Observability

SERVICE_NAME = "merchant_award-service"


@dataclass(frozen=True)
class Service:
    merchant_award_query: MerchantAwardQueryService
    merchant_award_command: MerchantAwardCommandService


def new_service(
    repos: Repositories,
    mencache: Mencache,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        merchant_award_query=MerchantAwardQueryServiceImpl(
            repos.merchant_award_query,
            mencache.merchant_award_query,
            logger,
            obs,
        ),
        merchant_award_command=MerchantAwardCommandServiceImpl(
            repos.merchant_award_command,
            mencache.merchant_award_command,
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]
