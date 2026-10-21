"""Gateway merchant_business routes."""

from service.apigateway.handler.merchant_business.command import (
    router as command_router,
)
from service.apigateway.handler.merchant_business.handler import (
    MerchantBusinessHandler,
)
from service.apigateway.handler.merchant_business.query import router as query_router

__all__ = ["MerchantBusinessHandler", "command_router", "query_router"]
