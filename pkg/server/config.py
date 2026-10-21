"""Common gRPC service configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ServerConfig:
    service_name: str
    port: int
    service_version: str = "0.1.0"
    environment: str = "development"
    otel_endpoint: str = "localhost:4317"
    enable_telemetry: bool = True
    enable_reflection: bool = False

    @property
    def host(self) -> str:
        return "0.0.0.0"


# Defaults kept from the server package.
DEFAULT_MAX_CONCURRENT_STREAMS = 1024
DEFAULT_KEEPALIVE_TIME = 20.0
DEFAULT_KEEPALIVE_TIMEOUT = 5.0
MONITORING_INTERVAL = 30.0
CLEANUP_INTERVAL = 120.0
CACHE_REF_COUNT_THRESHOLD = 500
SHUTDOWN_TIMEOUT = 30.0
