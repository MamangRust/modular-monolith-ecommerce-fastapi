"""Gateway review routes."""

from service.apigateway.handler.review.command import router as command_router
from service.apigateway.handler.review.handler import ReviewHandler
from service.apigateway.handler.review.query import router as query_router

__all__ = ["ReviewHandler", "command_router", "query_router"]
