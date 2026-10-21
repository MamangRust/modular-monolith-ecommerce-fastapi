"""Gateway merchant_social_link routes."""

from service.apigateway.handler.merchant_social_link.command import (
    router as command_router,
)
from service.apigateway.handler.merchant_social_link.handler import (
    MerchantSocialLinkHandler,
)

__all__ = ["MerchantSocialLinkHandler", "command_router"]
