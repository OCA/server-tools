from odoo.tools import config as odoo_config
from dataclasses import dataclass
from typing import Dict, Optional
import os

import logging

_logger = logging.getLogger(__name__)


PROTO_GRPC_AVAILABLE = False
try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter as OTLPSpanExporterGRPC,
    )
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
        OTLPMetricExporter as OTLPMetricExporterGRPC,
    )
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
        OTLPLogExporter as OTLPLogExporterGRPC,
    )

    PROTO_GRPC_AVAILABLE = True
except Exception:
    pass

PROTO_HTTP_AVAILABLE = False
try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
        OTLPSpanExporter as OTLPSpanExporterHTTP,
    )
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
        OTLPMetricExporter as OTLPMetricExporterHTTP,
    )
    from opentelemetry.exporter.otlp.proto.http._log_exporter import (
        OTLPLogExporter as OTLPLogExporterHTTP,
    )

    PROTO_HTTP_AVAILABLE = True
except Exception:
    pass


def _parse_keyvals(keyvals_str: Optional[str]) -> Dict[str, str]:
    """Helper to parse key=value,key=value strings into a dict"""
    keyvals = {}
    if keyvals_str:
        for keyval in keyvals_str.split(","):
            if "=" not in keyval:
                _logger.warning(f"Invalid key=value pair: {keyval}")
                continue
            key, value = keyval.split("=", 1)
            if key and value:
                keyvals[key.strip()] = value.strip()
    return keyvals


def _normalise_protocol(protocol: str) -> Optional[str]:
    """Map protocol options to standard values"""
    if protocol == "grpc":
        return "grpc"
    if protocol in ("http/protobuf", "http/proto", "http"):
        return "http/protobuf"
    _logger.warning(f"Unsupported protocol: {protocol}")
    return None


def _get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """Helper to get config values, checking env first, then Odoo config"""
    key_env = key
    key_conf = key[5:].lower()  # strip OTEL_ and lower
    otel_config = odoo_config.misc.get("otel", {})
    return os.getenv(key_env) or otel_config.get(key_conf) or default


@dataclass(frozen=True)
class OTelExporterConfig:
    protocol: str
    endpoint: str
    headers: Dict[str, str]
    grpc_insecure: Optional[bool] = None

    @staticmethod
    def load(
        signal: str,
        default_protocol: str,
        default_endpoint_http: str,
        default_endpoint_grpc: str,
        default_headers: Dict[str, str],
    ) -> Optional["OTelExporterConfig"]:
        sig = signal.upper()

        enable = _get_config(f"OTEL_EXPORTER_OTLP_{sig}_ENABLE", False)
        if not enable:
            return None

        proto = _normalise_protocol(
            _get_config(f"OTEL_EXPORTER_OTLP_{sig}_PROTOCOL", default_protocol)
        )
        if proto == "grpc" and not PROTO_GRPC_AVAILABLE:
            _logger.error(
                f"gRPC selected for {signal} but dependency is not installed. Hint:\n - pip install opentelemetry-exporter-otlp-proto-grpc"
            )
            return None

        if proto == "grpc":
            default_endpoint = default_endpoint_grpc
        elif proto == "http/protobuf":
            default_endpoint = default_endpoint_http
        else:
            _logger.error(f"Unsupported protocol for {signal}: {proto}")
            return None

        endpoint = _get_config(
            f"OTEL_EXPORTER_OTLP_{sig}_ENDPOINT",
            default_endpoint,
        )
        headers = (
            _parse_keyvals(
                _get_config(
                    f"OTEL_EXPORTER_OTLP_{sig}_HEADERS",
                    None,
                )
            )
            or default_headers
        )

        grpc_insecure = False
        if proto == "grpc":
            grpc_insecure = endpoint.startswith("http://")

        return OTelExporterConfig(
            protocol=proto,
            endpoint=endpoint,
            headers=headers,
            grpc_insecure=grpc_insecure,
        )


@dataclass(frozen=True)
class OTelConfig:
    enable: bool
    resource_attributes: Dict[str, str]
    traces_exporter: Optional[OTelExporterConfig]
    logs_exporter: Optional[OTelExporterConfig]
    metrics_exporter: Optional[OTelExporterConfig]

    @staticmethod
    def disabled() -> "OTelConfig":
        return OTelConfig(
            enable=False,
            resource_attributes={},
            traces_exporter=None,
            logs_exporter=None,
            metrics_exporter=None,
        )

    @staticmethod
    def load() -> "OTelConfig":
        if not PROTO_GRPC_AVAILABLE and not PROTO_HTTP_AVAILABLE:
            _logger.error(
                "No OTLP exporter available. Hint:\n"
                " - pip install opentelemetry-exporter-otlp-proto-grpc\n"
                " - pip install opentelemetry-exporter-otlp-proto-http"
            )
            return OTelConfig.disabled()

        enable = _get_config("OTEL_ENABLE", False)
        resource_attrs = _parse_keyvals(_get_config("OTEL_RESOURCE_ATTRIBUTES", ""))
        default_protocol = _normalise_protocol(
            _get_config("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
        )
        default_endpoint_http = _get_config(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318"
        )
        default_endpoint_grpc = _get_config(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"
        )
        default_headers = _parse_keyvals(_get_config("OTEL_EXPORTER_OTLP_HEADERS", ""))

        metrics_exporter = OTelExporterConfig.load(
            "METRICS",
            default_protocol,
            default_endpoint_http,
            default_endpoint_grpc,
            default_headers,
        )
        logs_exporter = OTelExporterConfig.load(
            "LOGS",
            default_protocol,
            default_endpoint_http,
            default_endpoint_grpc,
            default_headers,
        )
        traces_exporter = OTelExporterConfig.load(
            "TRACES",
            default_protocol,
            default_endpoint_http,
            default_endpoint_grpc,
            default_headers,
        )

        return OTelConfig(
            enable=enable,
            resource_attributes=resource_attrs,
            traces_exporter=traces_exporter,
            logs_exporter=logs_exporter,
            metrics_exporter=metrics_exporter,
        )
