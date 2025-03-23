import traceback

from celery import Task
from pytrends.request import TrendReq
from shared_utils.db.session import get_db
from shared_utils.schemas.status import TaskStatus
from shared_utils.async_handler import AsyncHandler

from app.repositories.task import update_task
from app.schemas.task import TrendResponseQListItem, TrendResponse, TrendError, TrendTaskUpdate


class TrendTask(Task):

    @staticmethod
    @AsyncHandler.with_async_generator(get_db)
    async def before_start(db, task_id, args, kwargs):
        await update_task(
            task_id=task_id,
            task_update=TrendResponse(
                status=TaskStatus.IN_PROGRESS
            ),
            db=db
        )

    @staticmethod
    @AsyncHandler.with_async_generator(get_db)
    async def on_success(db, retval, task_id, args, kwargs):
        await update_task(
            task_id=task_id,
            task_update=TrendTaskUpdate(
                status=TaskStatus.COMPLETED,
                result_data=[
                    TrendResponse(
                        date=retval['date'],
                        is_partial=retval['is_partial'],
                        q_list=[
                            TrendResponseQListItem(
                                query=q['query'],
                                value=q['value']
                            )
                            for q in retval['q_List']
                        ]
                    )
                ]
            ),
            db=db
        )

    @staticmethod
    @AsyncHandler.with_async_generator(get_db)
    async def on_failure(db, exc, task_id, args, kwargs, einfo):
        await update_task(
            task_id=task_id,
            task_update=TrendResponse(
                status=TaskStatus.FAILED,
                error=TrendError(
                    code=500,
                    error=traceback.format_exc()
                )
            ),
            db=db
        )

    @staticmethod
    @AsyncHandler.with_async_generator(get_db)
    async def on_retry(db, exc, task_id, args, kwargs, einfo):
        await update_task(
            task_id=task_id,
            task_update=TrendResponse(
                status=TaskStatus.RETRY,
                error=TrendError(
                    code=500,
                    error=traceback.format_exc()
                ),
                increment_retry_count=True
            ),
            db=db
        )
