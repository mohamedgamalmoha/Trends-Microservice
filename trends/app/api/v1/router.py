from fastapi import APIRouter

from app.api.v1.endpoints import task


v1_api_router = APIRouter(
    prefix='/v1'
)

v1_api_router.include_router(task.task_router)
