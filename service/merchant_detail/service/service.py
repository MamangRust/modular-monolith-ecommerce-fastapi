"""merchant_detail service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_detail.redis import Mencache
from service.merchant_detail.repository.repository import Repositories
from service.merchant_detail.service.interfaces import (
    MerchantDetailCommandService,
    MerchantDetailQueryService,
    MerchantSocialLinkCommandService,
)
from service.merchant_detail.service.merchant_detail_command_service import (
    MerchantDetailCommandServiceImpl,
)
from service.merchant_detail.service.merchant_detail_query_service import (
    MerchantDetailQueryServiceImpl,
)
from service.merchant_detail.service.merchant_social_link_command_service import (
    MerchantSocialLinkCommandServiceImpl,
)
from shared.observability import Observability

SERVICE_NAME = "merchant_detail-service"


@dataclass(frozen=True)
class Service:
    merchant_detail_query: MerchantDetailQueryService
    merchant_detail_command: MerchantDetailCommandService
    merchant_social_link_command: MerchantSocialLinkCommandService


def new_service(
    repos: Repositories,
    mencache: Mencache,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        merchant_detail_query=MerchantDetailQueryServiceImpl(
            repos.merchant_detail_query,
            mencache.merchant_detail_query,
            logger,
            obs,
        ),
        merchant_detail_command=MerchantDetailCommandServiceImpl(
            repos.merchant_detail_command,
            repos.merchant_query,
            mencache.merchant_detail_command,
            logger,
            obs,
        ),
        merchant_social_link_command=MerchantSocialLinkCommandServiceImpl(
            repos.merchant_social_link_command,
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]
