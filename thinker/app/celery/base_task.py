import traceback

from celery import Task
from celery.bin.control import status
from shared_utils.db.session import get_db
from shared_utils.schemas.status import TaskStatus
from shared_utils.async_handler import AsyncHandler

from app.services.task import TaskService, get_task_service
from app.schemas.task import ThinkResponse, ThinkError, ThinkTaskUpdate


class ThinkTask(Task):

    @staticmethod
    @AsyncHandler.with_async_generator(get_db)
    async def before_start(db, task_id, args, kwargs):
        task_service = TaskService(db=db)
        await task_service.update(
            id=task_id,
            status=TaskStatus.IN_PROGRESS
        )

    @staticmethod
    @AsyncHandler.with_async_generator(get_db)
    async def on_success(db, retval, task_id, args, kwargs):
        task_service = TaskService(db=db)
        await task_service.update(
            id=task_id,
            status=TaskStatus.COMPLETED,
            result_data=retval
        )

    @staticmethod
    @AsyncHandler.with_async_generator(get_db)
    async def on_failure(db, exc, task_id, args, kwargs, einfo):
        task_service = TaskService(db=db)
        await task_service.update(
            id=task_id,
            status=TaskStatus.FAILED,
            error={
                'code': 500,
                'error': traceback.format_exc()
            }
        )

    @staticmethod
    @AsyncHandler.with_async_generator(get_db)
    async def on_retry(db, exc, task_id, args, kwargs, einfo):
        task_service = TaskService(db=db)
        await task_service.update(
            id=task_id,
            status=TaskStatus.RETRY,
            error={
                'code': 500,
                'error': traceback.format_exc()
            }
        )
        await task_service.increment_retry_count(id=task_id, increment_by=1)
