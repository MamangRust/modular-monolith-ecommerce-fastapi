"""Gateway merchant document routes."""

from service.apigateway.handler.merchant_document.command import router as command_router
from service.apigateway.handler.merchant_document.handler import (
    MerchantDocumentHandler,
)
from service.apigateway.handler.merchant_document.query import router as query_router

__all__ = ["MerchantDocumentHandler", "command_router", "query_router"]
