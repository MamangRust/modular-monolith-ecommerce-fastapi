"""Order item service composition root.

No Kafka producer or consumer: repositories -> cache -> service -> handler ->
two servicers (query, command)."""

from __future__ import annotations

from pb.order_item import order_item_command_pb2_grpc, order_item_query_pb2_grpc
from pkg.config.settings import Settings, get_settings
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.order_item.handler import new_handler
from service.order_item.repository import new_repositories
from service.order_item.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "order_item-service"
SERVICE_PORT = 50056
ORDER_ITEM_SERVICE_NAMES = [
    "pb.order_item.OrderItemQueryService",
    "pb.order_item.OrderItemCommandService",
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
        order_item_query_pb2_grpc.add_OrderItemQueryServiceServicer_to_server(
            handler.order_item_query, server
        )
        order_item_command_pb2_grpc.add_OrderItemCommandServiceServicer_to_server(
            handler.order_item_command, server
        )

    srv.register_services = register
    srv.reflection_services = list(ORDER_ITEM_SERVICE_NAMES)
    return srv


__all__ = ["ORDER_ITEM_SERVICE_NAMES", "SERVICE_NAME", "SERVICE_PORT", "new_server"]
