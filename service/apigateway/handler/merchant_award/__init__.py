"""Gateway merchant_award routes."""

from service.apigateway.handler.merchant_award.command import router as command_router
from service.apigateway.handler.merchant_award.handler import MerchantAwardHandler
from service.apigateway.handler.merchant_award.query import router as query_router

__all__ = ["MerchantAwardHandler", "command_router", "query_router"]
