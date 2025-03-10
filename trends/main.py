from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.api.endpoints import task


app = FastAPI(
    lifespan=lifespan,
    docs_url='/api/tasks/docs',
    redoc_url='/api/tasks/redoc',
    openapi_url='/api/tasks/openapi.json'
)

app.include_router(task.task_router, prefix='/api')
