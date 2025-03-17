from celery import uuid
from fastapi import APIRouter, HTTPException

from app.core.conf import settings
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskRetrieve, ThinkResponse
from app.celery.tasks import think_task


task_router = APIRouter(
    tags=['question']
)


@task_router.post("/", response_model=TaskRetrieve)
async def create_task_route(task: TaskCreate):
    task_id = uuid()
    user_id = 0
    search_task_id = 0
    results = await think_task(
        question=task.question,
        context=task.context,
        temperature=task.temperature,
        max_tokens=task.max_tokens
    )
    return TaskRetrieve(
        task_id=task_id,
        user_id=user_id,
        search_task_id=search_task_id,
        question=task.question,
        context=task.context,
        temperature=task.temperature,
        max_tokens=task.max_tokens,
        schedule_at=task.schedule_at,
        status=TaskStatus.COMPLETED,
        result_data=ThinkResponse(
            answer=results['answer'],
            thinking=results['thinking']
        )
    )
