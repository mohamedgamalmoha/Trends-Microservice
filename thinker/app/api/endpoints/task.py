from celery import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

from app import messages
from app.db.session import get_db
from app.repositories.task import create_task
from app.schemas.user import User
from app.schemas.task import TaskCreate, TaskRetrieve
from app.celery.tasks import think_task
from app.api.deps import get_current_user


task_router = APIRouter(
    tags=['question']
)


@task_router.post("/", response_model=TaskRetrieve)
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
    
    think_task.apply_async(
        kwargs={
            "question": task.question,
            "context": task.context,
            "temperature": task.temperature,
            "max_tokens": task.max_tokens
        },
        task_id=task_id
    )

    return db_task
