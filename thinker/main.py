from app.api.endpoints.task import task_router
from app.api.endpoints.health import health_router

from fastapi import FastAPI
from shared_utils.core.lifespan import lifespan


app = FastAPI(
    lifespan=lifespan,
    docs_url='/api/think/docs',
    redoc_url='/api/think/redoc',
    openapi_url='/api/think/openapi.json'
)

app.include_router(task_router, prefix='/api/think')
app.include_router(health_router, prefix='/api/think')
