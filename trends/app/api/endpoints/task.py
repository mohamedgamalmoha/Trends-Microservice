from typing import List

from celery import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from shared_utils import messages
from shared_utils.db.session import get_db
from shared_utils.schemas.user import User
from shared_utils.api.deps.user import get_current_user, get_current_admin_user

from app.repositories.task import create_task, get_user_task_by_id, get_user_tasks, get_all_tasks, delete_task
from app.schemas.task import TaskCreate, TaskRetrieve
from app.celery.tasks import trends_search_task


task_router = APIRouter(
    tags = ['search']
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


@task_router.get("/tasks/", response_model=List[TaskRetrieve])
async def get_tasks_route(
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
    ):

    db_tasks = await get_all_tasks(db=db)

    return db_tasks


@task_router.delete("/{user_id}/task/{task_id}/", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_route(
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

    db_task = await get_user_task_by_id(
        user_id=user_id,
        task_id=task_id,
        db=db
    )

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.TASK_NOT_FOUND_MESSAGE
        )

    await delete_task(task_id=task_id, db=db)

    return None
