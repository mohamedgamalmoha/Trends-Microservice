from app.api.endpoints.health import health_router
from app.api.endpoints.question import question_router

from fastapi import FastAPI


app = FastAPI(
    docs_url='/'
)

app.include_router(health_router)
app.include_router(question_router) 
