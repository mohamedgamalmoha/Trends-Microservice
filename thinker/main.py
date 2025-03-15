from app.api.endpoints.health import health_router
from app.api.endpoints.question import question_router

from fastapi import FastAPI


app = FastAPI(
    docs_url='/api/think/docs',
    redoc_url='/api/think/redoc',
    openapi_url='/api/think/openapi.json'
)

app.include_router(health_router, prefix='/api/think')
app.include_router(question_router, prefix='/api/think')
