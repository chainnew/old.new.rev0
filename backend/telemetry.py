"""
OpenTelemetry initialization for Grok-orc Swarm Synergy.
Provides distributed tracing and metrics for orchestration visibility.

Phase 1B: Console exporter for demo (Week 1 adds Grafana/Jaeger)
"""
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentation
from opentelemetry.instrumentation.requests import RequestsInstrumentation
import os

# Service name for identifying spans/metrics
SERVICE_NAME = "grok-orc-orchestrator"

def init_telemetry(app=None):
    """
    Initialize OpenTelemetry for tracing and metrics.

    Args:
        app: FastAPI app instance (optional, for auto-instrumentation)

    Returns:
        (tracer, meter) tuple for manual instrumentation
    """
    # Resource attributes (service metadata)
    resource = Resource(attributes={
        "service.name": SERVICE_NAME,
        "service.version": "1.1.1",
        "deployment.environment": os.getenv("ENV", "development")
    })

    # === TRACING SETUP ===
    # Use console exporter for Phase 1B demo (swap to OTLP for Grafana)
    trace_provider = TracerProvider(resource=resource)

    # Console exporter for immediate visibility
    console_exporter = ConsoleSpanExporter()
    span_processor = BatchSpanProcessor(console_exporter)
    trace_provider.add_span_processor(span_processor)

    # Set global tracer provider
    trace.set_tracer_provider(trace_provider)

    # === METRICS SETUP ===
    # Console metric exporter (Phase 1B)
    metric_reader = PeriodicExportingMetricReader(
        ConsoleMetricExporter(),
        export_interval_millis=10000  # Export every 10s
    )
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader]
    )
    metrics.set_meter_provider(meter_provider)

    # === AUTO-INSTRUMENTATION ===
    # Instrument HTTP requests (for MCP tool calls)
    RequestsInstrumentation().instrument()

    # Instrument FastAPI if app provided
    if app:
        FastAPIInstrumentation.instrument_app(app)

    # Get tracer and meter for manual spans
    tracer = trace.get_tracer(__name__)
    meter = metrics.get_meter(__name__)

    print(f"✅ OpenTelemetry initialized for {SERVICE_NAME}")
    print(f"   📊 Traces: Console (demo mode)")
    print(f"   📈 Metrics: Console (10s interval)")

    return tracer, meter


# Global tracer/meter instances (import from other modules)
_tracer = None
_meter = None

def get_tracer():
    """Get global tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer(__name__)
    return _tracer

def get_meter():
    """Get global meter instance."""
    global _meter
    if _meter is None:
        _meter = metrics.get_meter(__name__)
    return _meter
