"""merchant_detail handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant_detail.handler.merchant_detail_command import (
    MerchantDetailCommandHandler,
)
from service.merchant_detail.handler.merchant_detail_query import (
    MerchantDetailQueryHandler,
)
from service.merchant_detail.handler.merchant_social_link_command import (
    MerchantSocialLinkCommandHandler,
)
from service.merchant_detail.service.service import Service


@dataclass(frozen=True)
class Handler:
    merchant_detail_query: MerchantDetailQueryHandler
    merchant_detail_command: MerchantDetailCommandHandler
    merchant_social_link_command: MerchantSocialLinkCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        merchant_detail_query=MerchantDetailQueryHandler(
            service.merchant_detail_query, logger
        ),
        merchant_detail_command=MerchantDetailCommandHandler(
            service.merchant_detail_command, logger
        ),
        merchant_social_link_command=MerchantSocialLinkCommandHandler(
            service.merchant_social_link_command, logger
        ),
    )


__all__ = ["Handler", "new_handler"]
