from typing import Sequence

from fastapi import Depends
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskRetrieve, TaskUpdate


async def create_task(task_id: str, task: TaskCreate, db: AsyncSession = Depends(get_db)) -> Task:
    request_data = task.request_data.custom_model_dump()

    db_task = Task(
        task_id=task_id,
        **task.model_dump(exclude=['request_data']),
        request_data=request_data
    )

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    return db_task


async def get_task_by_id(task_id: str, db: AsyncSession = Depends(get_db)) -> Task | None:
    result = await db.execute(
        select(Task).filter_by(task_id=task_id)
    )
    return result.scalar_one_or_none()


async def get_user_task_by_id(user_id: int, task_id: str, db: AsyncSession = Depends(get_db)) -> Task | None:
    result = await db.execute(
        select(Task).filter_by(user_id=user_id, task_id=task_id)
    )
    return result.scalar_one_or_none()


async def get_user_tasks(user_id: int, db: AsyncSession = Depends(get_db)) -> Sequence[Task]:
    result = await db.execute(
        select(Task).filter_by(user_id=user_id)
    )
    return result.scalars().all()


async def update_task(task_id: str, task_update: TaskUpdate, db: AsyncSession = Depends(get_db)) -> Task | None:
    db_task = await get_task_by_id(task_id=task_id, db=db)

    if not db_task:
        return None

    for field_name, new_field_value in task_update.model_dump().items():
        if new_field_value:
            setattr(db_task, field_name, new_field_value)

    await db.commit()
    await db.refresh(db_task)

    return db_task


async def increment_retry_count_task(task_id: str, increment: int = 1, db: AsyncSession = Depends(get_db)) -> Task | None:
    db_task = await get_task_by_id(task_id=task_id, db=db)

    if not db_task:
        return None

    db_task.retry_count += increment

    await db.commit()
    await db.refresh(db_task)

    return db_task


async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)) -> None:
    db_task = await get_task_by_id(task_id=task_id, db=db)

    if not db_task:
        return None

    await db.delete(db_task)
    await db.commit()
