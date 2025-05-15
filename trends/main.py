from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from shared_utils.core.lifespan import lifespan

from app.api.v1 import v1_api_router


app = FastAPI(
    lifespan=lifespan,
    docs_url='/api/search/docs',
    redoc_url='/api/search/redoc',
    openapi_url='/api/search/openapi.json'
)

app.include_router(v1_api_router, prefix='/api/search')


Instrumentator().instrument(app).expose(app)
