"""
OpenTelemetry initialization for Grok-orc Swarm Synergy.
Provides distributed tracing and metrics for orchestration visibility.

Phase 1B: Console exporter for demo
Week 4 Preview: Prometheus exporter for Grafana dashboards
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

# Week 4 Preview: Prometheus exporter
try:
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from prometheus_client import start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

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
    # Week 4 Preview: Use Prometheus exporter if available, fallback to console
    metric_readers = []

    if PROMETHEUS_AVAILABLE and os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true":
        # Prometheus exporter (Week 4 Preview)
        prometheus_reader = PrometheusMetricReader()
        metric_readers.append(prometheus_reader)

        # Start Prometheus HTTP server on port 8889
        prometheus_port = int(os.getenv("PROMETHEUS_PORT", "8889"))
        start_http_server(prometheus_port)
        print(f"   📊 Prometheus metrics server started on port {prometheus_port}")
    else:
        # Fallback to console exporter (Phase 1B default)
        console_reader = PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=10000  # Export every 10s
        )
        metric_readers.append(console_reader)

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=metric_readers
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
    if PROMETHEUS_AVAILABLE and os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true":
        print(f"   📈 Metrics: Prometheus (port {os.getenv('PROMETHEUS_PORT', '8889')})")
    else:
        print(f"   📈 Metrics: Console (10s interval)")

    return tracer, meter


def create_synergy_metrics(meter):
    """
    Create Week 4 synergy metrics for Grafana dashboards.

    Args:
        meter: OpenTelemetry meter instance

    Returns:
        dict of metric instruments
    """
    return {
        # Stack inference metrics
        "stack_confidence": meter.create_histogram(
            name="stack_confidence",
            description="Stack inference confidence scores (0-1)",
            unit="1"
        ),

        # UI inference metrics
        "ui_components_generated": meter.create_counter(
            name="ui_components_generated",
            description="Total UI components generated",
            unit="1"
        ),

        # Conflict resolution metrics
        "conflicts_detected": meter.create_counter(
            name="conflicts_detected",
            description="Total UI/Backend conflicts detected",
            unit="1"
        ),
        "conflicts_resolved": meter.create_counter(
            name="conflicts_resolved",
            description="Total conflicts successfully resolved",
            unit="1"
        ),
        "conflict_similarity": meter.create_histogram(
            name="conflict_similarity",
            description="pgvector cosine similarity scores for conflict detection",
            unit="1"
        ),

        # Visual test metrics
        "visual_tests_total": meter.create_counter(
            name="visual_tests_total",
            description="Total visual tests executed",
            unit="1"
        ),
        "visual_tests_passed": meter.create_counter(
            name="visual_tests_passed",
            description="Visual tests passed",
            unit="1"
        ),
        "visual_tests_failed": meter.create_counter(
            name="visual_tests_failed",
            description="Visual tests failed",
            unit="1"
        ),
        "visual_diff_score": meter.create_histogram(
            name="visual_diff_score",
            description="Screenshot diff scores (0-1, pixelmatch)",
            unit="1"
        ),

        # Workflow metrics
        "workflows_completed": meter.create_counter(
            name="workflows_completed",
            description="Total workflows completed",
            unit="1"
        ),
        "workflow_duration_seconds": meter.create_histogram(
            name="workflow_duration_seconds",
            description="End-to-end workflow duration",
            unit="s"
        ),

        # Cost metrics
        "openrouter_tokens_used": meter.create_counter(
            name="openrouter_tokens_used",
            description="Total OpenRouter tokens consumed",
            unit="1"
        )
    }


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
