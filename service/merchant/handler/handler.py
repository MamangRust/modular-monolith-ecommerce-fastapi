"""Merchant handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.merchant.handler.merchant_command import MerchantCommandHandler
from service.merchant.handler.merchant_document_command import (
    MerchantDocumentCommandHandler,
)
from service.merchant.handler.merchant_document_query import (
    MerchantDocumentQueryHandler,
)
from service.merchant.handler.merchant_query import MerchantQueryHandler
from service.merchant.service.service import Service


@dataclass(frozen=True)
class Handler:
    merchant_query: MerchantQueryHandler
    merchant_command: MerchantCommandHandler
    merchant_document_query: MerchantDocumentQueryHandler
    merchant_document_command: MerchantDocumentCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        merchant_query=MerchantQueryHandler(service.merchant_query, logger),
        merchant_command=MerchantCommandHandler(service.merchant_command, logger),
        merchant_document_query=MerchantDocumentQueryHandler(
            service.merchant_document_query, logger
        ),
        merchant_document_command=MerchantDocumentCommandHandler(
            service.merchant_document_command, logger
        ),
    )


__all__ = ["Handler", "new_handler"]
