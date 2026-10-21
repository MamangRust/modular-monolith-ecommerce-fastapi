"""Gateway slider routes."""

from service.apigateway.handler.slider.command import router as command_router
from service.apigateway.handler.slider.handler import SliderHandler
from service.apigateway.handler.slider.query import router as query_router

__all__ = ["SliderHandler", "command_router", "query_router"]
