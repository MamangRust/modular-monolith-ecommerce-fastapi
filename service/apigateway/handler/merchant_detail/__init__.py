"""Gateway merchant_detail routes."""

from service.apigateway.handler.merchant_detail.command import (
    router as command_router,
)
from service.apigateway.handler.merchant_detail.handler import MerchantDetailHandler
from service.apigateway.handler.merchant_detail.query import router as query_router

__all__ = ["MerchantDetailHandler", "command_router", "query_router"]
