"""Merchant service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.database.database import Database
from pkg.kafka.kafka import Kafka
from pkg.logger.logger import Logger
from service.merchant.redis import Mencache
from service.merchant.repository.repository import Repositories
from service.merchant.service.interfaces import (
    MerchantCommandService,
    MerchantDocumentCommandService,
    MerchantDocumentQueryService,
    MerchantQueryService,
)
from service.merchant.service.merchant_command_service import (
    MerchantCommandServiceImpl,
)
from service.merchant.service.merchant_document_command_service import (
    MerchantDocumentCommandServiceImpl,
)
from service.merchant.service.merchant_document_query_service import (
    MerchantDocumentQueryServiceImpl,
)
from service.merchant.service.merchant_query_service import MerchantQueryServiceImpl
from shared.observability import Observability

SERVICE_NAME = "merchant-service"


@dataclass(frozen=True)
class Service:
    merchant_query: MerchantQueryService
    merchant_command: MerchantCommandService
    merchant_document_command: MerchantDocumentCommandService
    merchant_document_query: MerchantDocumentQueryService


def new_service(
    repos: Repositories,
    mencache: Mencache,
    db: Database,
    kafka: Kafka | None,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        merchant_query=MerchantQueryServiceImpl(
            repos.merchant_query, mencache.merchant_query, logger, obs
        ),
        merchant_command=MerchantCommandServiceImpl(
            repos.merchant_command,
            repos.merchant_query,
            repos.user_query,
            mencache.merchant_command,
            db,
            kafka,
            logger,
            obs,
        ),
        merchant_document_command=MerchantDocumentCommandServiceImpl(
            repos.merchant_document_command,
            repos.merchant_query,
            repos.user_query,
            mencache.merchant_document_command,
            db,
            logger,
            obs,
        ),
        merchant_document_query=MerchantDocumentQueryServiceImpl(
            repos.merchant_document_query,
            mencache.merchant_document_query,
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]
