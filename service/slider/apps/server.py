"""Slider service composition root.

The slider domain has no Kafka consumer or producer, so the composition is just
repositories -> cache -> service -> handler -> servicers."""

from __future__ import annotations

from pb.slider import slider_command_pb2_grpc, slider_query_pb2_grpc
from pkg.config.settings import Settings, get_settings
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.slider.handler import new_handler
from service.slider.repository import new_repositories
from service.slider.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "slider-service"
SERVICE_PORT = 50062
SLIDER_SERVICE_NAMES = [
    "pb.slider.SliderQueryService",
    "pb.slider.SliderCommandService",
]


async def new_server(settings: Settings | None = None) -> GRPCServer:
    resolved = settings or get_settings()
    config = ServerConfig(
        service_name=SERVICE_NAME,
        port=SERVICE_PORT,
        environment=resolved.app.env,
        otel_endpoint=resolved.app.otel_endpoint,
        enable_telemetry=resolved.app.otel_enabled,
        enable_reflection=resolved.app.enable_reflection,
    )

    srv = await new_grpc_server(config, resolved.database)
    assert srv.db is not None

    redis = await new_redis_client(resolved.redis, SERVICE_NAME, srv.logger)
    srv.redis = redis
    cache_store = CacheStore(redis, srv.logger)

    repos = new_repositories(srv.db)
    service = new_service(repos, cache_store, srv.logger)
    handler = new_handler(service, srv.logger)

    def register(server) -> None:
        slider_query_pb2_grpc.add_SliderQueryServiceServicer_to_server(
            handler.slider_query, server
        )
        slider_command_pb2_grpc.add_SliderCommandServiceServicer_to_server(
            handler.slider_command, server
        )

    srv.register_services = register
    srv.reflection_services = list(SLIDER_SERVICE_NAMES)
    return srv


__all__ = ["SERVICE_NAME", "SERVICE_PORT", "SLIDER_SERVICE_NAMES", "new_server"]
