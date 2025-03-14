from typing import List

from celery import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from app import messages
from app.db.session import get_db
from app.repositories.task import create_task, get_user_task_by_id, get_user_tasks
from app.schemas.user import User
from app.schemas.task import TaskCreate, TaskRetrieve
from app.celery.tasks import trends_search_task
from app.api.deps import get_current_user


task_router = APIRouter(
    prefix='/tasks',
    tags = ['tasks']
)


@task_router.post('/', response_model=TaskRetrieve)
async def create_task_route(
        task: TaskCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):

    if not current_user.is_admin and task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

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
async def get_task_route(
        user_id: int,
        task_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):

    if not current_user.is_admin and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    db_task = await get_user_task_by_id(user_id=user_id, task_id=task_id, db=db)

    if db_task:
        return db_task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=messages.TASK_NOT_FOUND_MESSAGE
    )


@task_router.get("/{user_id}/tasks/", response_model=List[TaskRetrieve])
async def get_user_tasks_route(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):

    if not current_user.is_admin and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    return await get_user_tasks(user_id=user_id, db=db)
