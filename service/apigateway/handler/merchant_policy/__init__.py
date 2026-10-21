"""Gateway merchant_policy routes."""

from service.apigateway.handler.merchant_policy.command import router as command_router
from service.apigateway.handler.merchant_policy.handler import MerchantPolicyHandler
from service.apigateway.handler.merchant_policy.query import router as query_router

__all__ = ["MerchantPolicyHandler", "command_router", "query_router"]
