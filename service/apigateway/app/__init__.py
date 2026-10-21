"""FastAPI gateway application."""

from service.apigateway.app.app import SERVICE_NAME, create_app, lifespan

__all__ = ["SERVICE_NAME", "create_app", "lifespan"]
