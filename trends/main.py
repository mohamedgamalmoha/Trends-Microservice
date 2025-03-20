from fastapi import FastAPI
from shared_utils.core.lifespan import lifespan

from app.api.endpoints import task


app = FastAPI(
    lifespan=lifespan,
    docs_url='/api/search/docs',
    redoc_url='/api/search/redoc',
    openapi_url='/api/search/openapi.json'
)

app.include_router(task.task_router, prefix='/api/search')
