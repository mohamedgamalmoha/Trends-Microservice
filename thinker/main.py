from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from shared_utils.core.lifespan import lifespan

from app.api.endpoints.task import task_router
from app.api.endpoints.health import health_router


app = FastAPI(
    lifespan=lifespan,
    docs_url='/api/think/docs',
    redoc_url='/api/think/redoc',
    openapi_url='/api/think/openapi.json'
)

app.include_router(task_router, prefix='/api/think')
app.include_router(health_router, prefix='/api/think')


Instrumentator().instrument(app).expose(app, endpoint='/api/think/metrics')
