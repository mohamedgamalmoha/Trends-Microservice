import traceback
from datetime import datetime

from celery import Task
from pytrends.request import TrendReq
from shared_utils.db.session import get_db
from shared_utils.schemas.status import TaskStatus
from shared_utils.async_handler import AsyncHandler

from app.repositories.task import update_task
from app.schemas.task import TaskUpdate


class TrendTask(Task):

    @AsyncHandler.with_async_generator(get_db)
    async def on_success(self, db, retval, task_id, args, kwargs):
        await update_task(
            task_id=task_id,
            task_update=TaskUpdate(
                status=TaskStatus.COMPLETED,
                result_data=retval,
                updated_at=datetime.now()
            ),
            db=db
        )

    @AsyncHandler.with_async_generator(get_db)
    async def after_return(self, db, status, retval, task_id, args, kwargs, einfo):
        await update_task(
            task_id=task_id,
            task_update=TaskUpdate(
                updated_at=datetime.now()
            ),
            db=db
        )

    @AsyncHandler.with_async_generator(get_db)
    async def on_retry(self, db, exc, task_id, args, kwargs, einfo):
        await update_task(
            task_id=task_id,
            task_update=TaskUpdate(
                status=TaskStatus.IN_PROGRESS,
                error_message=str(exc),
                updated_at=datetime.now()
            ),
            increment=1,
            db=db
        )

    @AsyncHandler.with_async_generator(get_db)
    async def on_failure(self, db, exc, task_id, args, kwargs, einfo):
        await update_task(
            task_id=task_id,
            task_update=TaskUpdate(
                status=TaskStatus.FAILED,
                error_message=str(exc),
                result_data={
                    'error_type': type(exc).__name__,
                    'error_details': str(exc),
                    'traceback': traceback.format_exc()
                },
                updated_at=datetime.now()
            ),
            db=db
        )
