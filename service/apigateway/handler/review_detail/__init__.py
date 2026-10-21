"""Gateway review_detail routes."""

from service.apigateway.handler.review_detail.command import router as command_router
from service.apigateway.handler.review_detail.handler import ReviewDetailHandler
from service.apigateway.handler.review_detail.query import router as query_router

__all__ = ["ReviewDetailHandler", "command_router", "query_router"]
