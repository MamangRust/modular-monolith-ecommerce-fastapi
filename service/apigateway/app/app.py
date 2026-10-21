"""FastAPI gateway composition. Owns long-lived resources: managed gRPC channels to every domain service and Redis (response caches + role cache). Domain routers register themselves against the app; a domain that is not enabled (no address) simply contributes no routes, so the gateway can start against a partial deployment."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from pkg.auth.token import new_manager
from pkg.config.settings import get_settings
from pkg.logger.logger import Logger, get_logger
from pkg.otel import Telemetry, TelemetryConfig
from pkg.redis.redis import close_redis, new_redis_client
from pkg.upload_image import new_image_upload
from service.apigateway.app.client import ServiceConnections, connect
from service.apigateway.middlewares import JwtAuthMiddleware, RoleValidatorGRPC
from service.apigateway.redis.role import RoleCache
from shared.cache import CacheStore
from shared.errors.api_error import register_exception_handlers

SERVICE_NAME = "api-gateway"


class GatewayState:
    """Long-lived resources shared by all routers."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger: Logger = get_logger(SERVICE_NAME)
        self.connections: ServiceConnections | None = None
        self.redis: Any = None
        self.telemetry: Telemetry | None = None
        self.role_validator: RoleValidatorGRPC | None = None


_state: GatewayState | None = None


def state() -> GatewayState:
    if _state is None:
        raise RuntimeError("gateway state not initialized; app not started")
    return _state


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _state
    gateway = GatewayState()
    _state = gateway
    logger = gateway.logger
    settings = gateway.settings

    telemetry = Telemetry(
        TelemetryConfig(
            service_name=SERVICE_NAME,
            environment=settings.app.env,
            endpoint=settings.app.otel_endpoint,
            insecure=True,
            enabled=settings.app.otel_enabled,
        ),
        logger,
    )
    telemetry.init()
    gateway.telemetry = telemetry
    telemetry.instrument_fastapi(app)

    # Attributes read by routers at request time (see each get_*_handler).
    app.state.logger = logger
    app.state.settings = settings
    app.state.token_manager = new_manager(
        settings.app.require_secret_key(SERVICE_NAME)
    )

    # gRPC channels to every domain service.
    connections = await connect(settings.grpc, logger)
    gateway.connections = connections
    app.state.connections = connections

    # Redis-backed response caches (one logical DB for the gateway).
    redis = await new_redis_client(settings.redis, "apigateway", logger)
    gateway.redis = redis
    app.state.redis = redis
    cache_store = CacheStore(redis, logger)
    app.state.cache_store = cache_store

    # gateway's injected `upload_image.ImageUploads`).
    app.state.upload_image = new_image_upload(logger)

    # Direct-gRPC role validation over the role channel.
    role_validator = RoleValidatorGRPC(
        connections.channel("role"), RoleCache(cache_store, logger), logger
    )
    gateway.role_validator = role_validator
    app.state.role_validator = role_validator

    logger.info("gateway starting")
    try:
        yield
    finally:
        await connections.close()
        await close_redis(redis, logger)
        await telemetry.shutdown()
        logger.info("gateway stopped")
        _state = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ecommerce API",
        version="0.1.0",
        lifespan=lifespan,
    )
    register_exception_handlers(app)

    from fastapi.middleware.cors import CORSMiddleware

    from service.apigateway.app.health import register_health
    from service.apigateway.handler import register_routers

    # JWT first so CORSMiddleware ends up outermost (preflight short-circuits
    # before authentication).
    app.add_middleware(JwtAuthMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_health(app)
    register_routers(app)
    return app
