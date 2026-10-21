"""Role service composition root. Kafka being unavailable is logged and non-fatal, so the gRPC surface still serves reads/writes; it only disables role validation replies."""

from __future__ import annotations

from pb.role import role_command_pb2_grpc, role_query_pb2_grpc
from pkg.config.settings import Settings, get_settings
from pkg.kafka.kafka import Kafka
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.role.handler import new_handler
from service.role.kafka.role_consumer import (
    CONSUMER_GROUP,
    REQUEST_TOPIC,
    RoleKafkaHandler,
)
from service.role.repository import new_repositories
from service.role.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "role-service"
SERVICE_PORT = 50052
ROLE_SERVICE_NAMES = ["pb.role.RoleService", "pb.role.RoleCommandService"]


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

    kafka = Kafka(srv.logger, resolved.kafka.broker_list)
    try:
        await kafka.start()
    except Exception as exc:
        srv.logger.error("kafka producer start failed; continuing without events", error=str(exc))
    else:
        srv.add_cleanup_hook(kafka.close)
        consumer = RoleKafkaHandler(service.role_query, kafka, srv.logger)
        try:
            await kafka.start_consumers(
                [REQUEST_TOPIC],
                CONSUMER_GROUP,
                consumer.handle,
                manual_commit=True,
            )
        except Exception as exc:
            srv.logger.error("role consumer start failed; continuing without it", error=str(exc))

    handler = new_handler(service, srv.logger)

    def register(server) -> None:
        role_query_pb2_grpc.add_RoleQueryServiceServicer_to_server(handler.role_query, server)
        role_command_pb2_grpc.add_RoleCommandServiceServicer_to_server(
            handler.role_command, server
        )

    srv.register_services = register
    srv.reflection_services = list(ROLE_SERVICE_NAMES)
    return srv


__all__ = ["ROLE_SERVICE_NAMES", "SERVICE_NAME", "SERVICE_PORT", "new_server"]
