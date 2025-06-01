import traceback
from typing import Any, Dict

import requests
from celery import Task
from billiard.einfo import ExceptionInfo
from shared_utils.schemas.status import TaskStatus

from app.core.conf import settings
from app.core.security import create_task_signature


class ThinkTask(Task):

    @staticmethod
    def _get_request_headers(task_id: str) -> Dict[str, str]:
        """
        Helper method to get the headers for the request.
        
        Args:
            - task_id (str): Unique id of the task.
        
        Returns:
            - Dict: Headers for the request.
        """
        signature = create_task_signature(message=task_id)
        return {
            "Content-Type": "application/json",
            "X-Signature": signature
        }

    def _send_request(self, task_id: str, pyload: Dict[str, Any]) -> None:
        """
        Helper method to send a request to the task service.

        Args:
            - task_id (str): Unique id of the task.
            - pyload (Dict): Data to be sent in the request.
        """
        requests.put(
            f'{settings.TASK_CALLBACK_URL}/task/{task_id}/callback/',
            headers=self._get_request_headers(task_id),
            json=pyload
        )

    def before_start(self, task_id: str, args: tuple, kwargs: dict) -> None:
        """
        Handler called before the task starts.

        Args:
            - task_id (str): Unique id of the task.
            - args (Tuple): Original Args for the task.
            - kwargs (Dict): Original keyword Args for the task.
        """
        self._send_request(
            task_id=task_id,
            pyload={
                'status': TaskStatus.IN_PROGRESS.value,
                'increment_retry_count': True,
            }
        )

    def on_retry(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: ExceptionInfo) -> None:
        """
        Retry handler.

        This is run by the worker when the task is retried.

        Args:
            - exc (Exception): The exception raised by the task.
            - task_id (str): Unique id of the retried task.
            - args (Tuple): Original Args for the task that is being retried.
            - kwargs (Dict): Original keyword Args for the task that is being retried.
            - einfo (ExceptionInfo): Exception information.
        """
        self._send_request(
            task_id=task_id,
            pyload={
                'status': TaskStatus.RETRY.value,
                'error': {
                    'code': 500,
                    'error': traceback.format_exc()
                },
                'increment_retry_count': True
            }
        )

    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict) -> None:
        """
        Success handler.

        This is run by the worker when the task completes successfully.

        Args:
            - retval (Any): The return value of the task.
            - task_id (str): Unique id of the completed task.
            - args (Tuple): Original Args for the task that completed.
            - kwargs (Dict): Original keyword Args for the task that completed.
        """
        self._send_request(
            task_id=task_id,
            pyload={
                'status': TaskStatus.COMPLETED.value,
                'result_data': retval
            }
        )

    def on_failure(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: ExceptionInfo) -> None:
        """
        Error handler.

        This is run by the worker when the task fails.

        Args:
            - exc (Exception): The exception raised by the task.
            - task_id (str): Unique id of the failed task.
            - args (Tuple): Original Args for the task that failed.
            - kwargs (Dict): Original keyword Args for the task that failed.
            - einfo (ExceptionInfo): Exception information.
        """
        self._send_request(
            task_id=task_id,
            pyload={
                'status': TaskStatus.FAILED.value,
                'error': {
                    'code': 500,
                    'error': traceback.format_exc()
                }
            }
        )
