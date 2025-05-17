from fastapi import APIRouter

from app.api.v1.endpoints import task, health


v1_api_router = APIRouter(
    prefix='/v1'
)

v1_api_router.include_router(task.task_router)
v1_api_router.include_router(health.health_router)
