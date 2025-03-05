from typing import List

from celery import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from app import messages
from app.db.session import get_db
from app.repositories.task import create_task, get_user_task_by_id, get_user_tasks
from app.schemas.task import TaskCreate, TaskRetrieve
from app.tasks import trends_search_task


task_router = APIRouter(
    prefix='/tasks',
    tags = ['tasks']
)


@task_router.post('/', response_model=TaskRetrieve)
async def create_task_route(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    task_id = uuid()

    db_task = await create_task(
        task_id=task_id,
        task=task,
        db=db
    )

    trends_search_task.apply_async(
        kwargs=task.request_data.custom_model_dump(),
        task_id=task_id
    )

    return db_task


@task_router.get('/{user_id}/task/{task_id}/', response_model=TaskRetrieve)
async def get_task_route(user_id: int, task_id: str, db: AsyncSession = Depends(get_db)):
    db_task = await get_user_task_by_id(user_id=user_id, task_id=task_id, db=db)

    if db_task:
        return db_task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=messages.TASK_NOT_FOUND_MESSAGE
    )


@task_router.get("/{user_id}/tasks/", response_model=List[TaskRetrieve])
async def get_user_tasks_route(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_user_tasks(user_id=user_id, db=db)
