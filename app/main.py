"""Honeycomb telemetry demo — FastAPI service instrumented with OpenTelemetry.

Sends traces to Honeycomb via the OTLP/HTTP exporter.
"""

import os
import time
import uuid

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

HONEYCOMB_API_KEY = os.getenv("HONEYCOMB_API_KEY", "")
HONEYCOMB_DATASET = os.getenv("HONEYCOMB_DATASET", "fastapi-demo")
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://api.honeycomb.io")

resource = Resource.create(
    {
        "service.name": "fastapi-honeycomb-demo",
        "service.version": "1.0.0",
        "deployment.environment": "dev",
    }
)

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint=f"{OTEL_ENDPOINT}/v1/traces",
        headers={"x-honeycomb-team": HONEYCOMB_API_KEY},
    )
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

app = FastAPI(title="Honeycomb Telemetry Demo")
FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer(__name__)


def process_order(order_id: str) -> dict:
    """Simulated business logic, wrapped in its own span."""
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        time.sleep(0.05)  # simulated work
        with tracer.start_as_current_span("charge_payment"):
            time.sleep(0.02)
        return {"order_id": order_id, "status": "processed"}


@app.get("/")
def root() -> dict:
    return {"message": "Telemetry is flowing to Honeycomb"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/orders")
def create_order() -> dict:
    order_id = str(uuid.uuid4())
    return process_order(order_id)


@app.get("/flaky")
def flaky() -> dict:
    """Endpoint that randomly fails, so you can see errors in Honeycomb."""
    import random

    if random.random() < 0.5:
        raise RuntimeError("random failure for demo purposes")
    return {"status": "lucky this time"}


@app.on_event("shutdown")
def shutdown() -> None:
    provider.force_flush()
