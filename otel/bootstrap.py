from .config import OTelConfig

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
import logging

_logger = logging.getLogger(__name__)


def _build_resource(resource_attributes: dict) -> Resource:
    return Resource(attributes=resource_attributes)


def _init_tracing(config: OTelConfig):
    if not config.traces_exporter:
        _logger.info("OpenTelemetry tracing is not configured, skipping")
        return

    resource = _build_resource(config.resource_attributes)
    provider = TracerProvider(resource=resource)

    if config.traces_exporter.protocol == "grpc":
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        exporter = OTLPSpanExporter(
            endpoint=config.traces_exporter.endpoint,
            headers=config.traces_exporter.headers,
            insecure=config.traces_exporter.grpc_insecure,
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
    elif config.traces_exporter.protocol == "http/protobuf":
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )

        exporter = OTLPSpanExporter(
            endpoint=config.traces_exporter.endpoint,
            headers=config.traces_exporter.headers,
        )
        provider.add_span_processor(SimpleSpanProcessor(exporter))
    else:
        _logger.error(
            f"Invalid traces exporter protocol: {config.traces_exporter.protocol}"
        )
        return

    trace.set_tracer_provider(provider)
    _logger.info("OpenTelemetry tracing initialized")


def _init_metrics(config: OTelConfig):
    if not config.metrics_exporter:
        _logger.info("OpenTelemetry metrics export is not configured, skipping")
        return

    _logger.warning(
        "OpenTelemetry metrics export is configured but not implemented yet"
    )


def _init_logs(config: OTelConfig):
    if not config.logs_exporter:
        _logger.info("OpenTelemetry logs export is not configured, skipping")
        return

    _logger.warning("OpenTelemetry logs export is configured but not implemented yet")


_OTEL_INITIALIZED = False


def init_otel():
    global _OTEL_INITIALIZED
    if _OTEL_INITIALIZED:
        return

    config = OTelConfig.load()
    if not config.enable:
        _logger.info("OpenTelemetry is disabled by configuration")
        return

    _init_tracing(config)
    _init_metrics(config)
    _init_logs(config)

    _OTEL_INITIALIZED = True
