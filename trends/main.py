from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from shared_utils.core.lifespan import lifespan
from shared_utils.db.session import engine

from app.core.conf import settings
from app.api.v1 import v1_api_router


# OpenTelemetry setup
resource = Resource.create({
    SERVICE_NAME: settings.SERVICE_NAME,
    SERVICE_VERSION: settings.SERVICE_VERSION,
})
tracer_provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(
    endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
    insecure=settings.OTEL_EXPORTER_OTLP_INSECURE
)
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)


# FastAPI application setup
app = FastAPI(
    lifespan=lifespan,
    docs_url='/api/search/docs',
    redoc_url='/api/search/redoc',
    openapi_url='/api/search/openapi.json'
)

app.include_router(v1_api_router, prefix='/api')


# Instrument Prometheus
Instrumentator().instrument(app).expose(app, endpoint='/api/search/metrics')

# Instrument FastAPI
EXCLUDED_URLS = [
    "/api/search/metrics",
    "/api/search/docs",
    "/api/search/redoc",
    "/api/search/openapi.json"
]
FastAPIInstrumentor.instrument_app(app, excluded_urls=",".join(EXCLUDED_URLS))

# Instrument SQLAlchemy
SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

# Instrument HTTPX
HTTPXClientInstrumentor().instrument()
