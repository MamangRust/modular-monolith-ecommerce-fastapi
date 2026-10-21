"""merchant_business service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_business.redis import Mencache
from service.merchant_business.repository.repository import Repositories
from service.merchant_business.service.interfaces import (
    MerchantBusinessCommandService,
    MerchantBusinessQueryService,
)
from service.merchant_business.service.merchant_business_command_service import (
    MerchantBusinessCommandServiceImpl,
)
from service.merchant_business.service.merchant_business_query_service import (
    MerchantBusinessQueryServiceImpl,
)
from shared.observability import Observability

SERVICE_NAME = "merchant_business-service"


@dataclass(frozen=True)
class Service:
    merchant_business_query: MerchantBusinessQueryService
    merchant_business_command: MerchantBusinessCommandService


def new_service(
    repos: Repositories,
    mencache: Mencache,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        merchant_business_query=MerchantBusinessQueryServiceImpl(
            repos.merchant_business_query,
            mencache.merchant_business_query,
            logger,
            obs,
        ),
        merchant_business_command=MerchantBusinessCommandServiceImpl(
            repos.merchant_business_command,
            mencache.merchant_business_command,
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]
