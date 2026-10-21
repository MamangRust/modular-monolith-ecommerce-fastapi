"""OpenTelemetry bootstrap. A `Resource` labels every span/metric with `service.name` so the era dashboards can be reproduced against the Python services (see observability/grafana/provisioning/dashboards/)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pkg.logger.logger import Logger


@dataclass
class TelemetryConfig:
    service_name: str
    service_version: str = "0.1.0"
    environment: str = "development"
    endpoint: str = "localhost:4317"
    insecure: bool = True
    enabled: bool = True


class Telemetry:
    """Lazily initializes the OTel SDK when enabled. The gateway installs FastAPI/aiokafka/gRPC instrumentors from the same manager; domain gRPC services use it for spans + metrics only."""

    def __init__(self, config: TelemetryConfig, logger: Logger) -> None:
        self._config = config
        self._logger = logger
        self._tracer_provider: Any = None
        self._meter_provider: Any = None
        self._started = False

    @property
    def enabled(self) -> bool:
        return self._config.enabled

    def _resource(self) -> Any:
        from opentelemetry.sdk.resources import (
            DEPLOYMENT_ENVIRONMENT,
            SERVICE_NAME,
            SERVICE_VERSION,
            Resource,
        )

        return Resource.create(
            {
                SERVICE_NAME: self._config.service_name,
                SERVICE_VERSION: self._config.service_version,
                DEPLOYMENT_ENVIRONMENT: self._config.environment,
            }
        )

    def init(self) -> None:
        if not self._config.enabled or self._started:
            return
        try:
            from opentelemetry import metrics, trace
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
                OTLPMetricExporter,
            )
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.metrics.export import (
                PeriodicExportingMetricReader,
            )
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            resource = self._resource()

            tracer_provider = TracerProvider(resource=resource)
            tracer_provider.add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(
                        endpoint=self._config.endpoint,
                        insecure=self._config.insecure,
                    )
                )
            )
            trace.set_tracer_provider(tracer_provider)
            self._tracer_provider = tracer_provider

            metric_exporter = OTLPMetricExporter(
                endpoint=self._config.endpoint,
                insecure=self._config.insecure,
            )
            reader = PeriodicExportingMetricReader(
                metric_exporter, export_interval_millis=10_000
            )
            meter_provider = MeterProvider(
                resource=resource, metric_readers=[reader]
            )
            metrics.set_meter_provider(meter_provider)
            self._meter_provider = meter_provider

            self._started = True
            self._logger.info(
                "telemetry initialized",
                endpoint=self._config.endpoint,
                service=self._config.service_name,
            )
        except Exception as exc:  # telemetry must never block startup
            self._logger.warn(
                "telemetry init failed; continuing without it", error=str(exc)
            )

    def instrument_fastapi(self, app: Any) -> None:
        """Instrument a FastAPI app for HTTP spans + server metrics."""
        if not self._started:
            return
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(app)
        except Exception as exc:
            self._logger.warn("fastapi instrumentation failed", error=str(exc))

    def instrument_grpc_server(self) -> None:
        """Instrument all grpc.aio servers created afterwards."""
        if not self._started:
            return
        try:
            from opentelemetry.instrumentation.grpc import (
                GrpcAioInstrumentorServer,
            )

            GrpcAioInstrumentorServer().instrument()
        except Exception as exc:
            self._logger.warn("grpc server instrumentation failed", error=str(exc))

    async def shutdown(self) -> None:
        if self._tracer_provider is not None:
            self._tracer_provider.shutdown()
        if self._meter_provider is not None:
            self._meter_provider.shutdown()
        self._logger.info("telemetry shutdown")


__all__ = ["Telemetry", "TelemetryConfig"]
