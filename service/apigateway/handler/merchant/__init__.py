"""Gateway merchant routes."""

from service.apigateway.handler.merchant.command import router as command_router
from service.apigateway.handler.merchant.handler import MerchantHandler
from service.apigateway.handler.merchant.query import router as query_router

__all__ = ["MerchantHandler", "command_router", "query_router"]
