from typing import Generic, Sequence

from fastapi import Depends
from pydantic import BaseModel
from shared_utils.pagination import Paginator

from app.models.task import Task
from app.repositories.task import TaskModelRepository, get_task_repository


class TaskService:
    """
    Service class for managing task-related operations.
    This class provides asynchronous methods to create, retrieve, update, and delete task records.
    It interacts with a task repository to perform database operations.
    """

    def __init__(self, task_repository: TaskModelRepository) -> None:
        """
        Initialize the TaskService with a task repository.

        Args:
            - task_repository (TaskModelRepository): The repository used to interact with task data.
        """
        self.task_repository = task_repository

    async def create(self, id: str, user_id: str, q: str, **other_fields):
        """
        Create a new task.

        Args:
            - id (str): Task id to create.
            - username (str): Task user_id to create.
            - q (str): Task q to create.
            - **other_fields: Remaining fields to create.

        Returns:
            - Task: The created task instance.

        Raises:
            - ObjAlreadyExist: If a task with the same id exists.
        """
        return await self.task_repository.create(id=id, user_id=user_id, q=q, **other_fields)

    async def get_all(self) -> Sequence[Task]:
        """
        Retrieve all task instances.

        Returns:
            - Sequence[Task]: A sequence of all task instances.
        """
        return await self.task_repository.get_all()

    async def filter_by_user_id(self, user_id: str) -> Sequence[Task]:
        """
        Filter tasks by user_id.

        Args:
            - user_id (str): User id to filter tasks by.

        Returns:
            - Sequence[Task]: A sequence of task instances filtered by user_id.
        """
        return await self.task_repository.filter_by(user_id=user_id)

    async def get_by_id(self, id: str) -> Task:
        """
        Retrieves a single task instance by id.

        Args:
            - id (str): Task id to search for.

        Returns:
            - Task: The task instance if found.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        return await self.task_repository.get_by_id(id=id)

    async def get_by_user_id(self, id: str, user_id: str) -> Task:
        """
        Get task by task id & user id.

        Args:
            - id (str): Task id to search for.
            - user_id (str): User id to search for.

        Returns:
            - Task: The task instance if found.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        return await self.task_repository.get_by_user_id(id=id, user_id=user_id)

    async def get_paginated[Schema: BaseModel](
        self,
        paginator: Paginator,
        query_params: BaseModel,
        response_schema: Schema,
        **filters
    ) -> Generic[Schema]:
        """
        Retrieve paginated results from the task repository based on provided parameters.

        This method serves as a pass-through to the underlying task repository's get_paginated method,
        forwarding all parameters and returning the paginated results in the specified schema format.

        Args:
            - paginator (Paginator): A paginator class responsible for applying pagination logic to the query and response.
            - query_params (BaseModel): A Pydantic model containing query parameters for filtering.
            - response_schema (Schema): A Pydantic model class that defines the structure of the response items.
            - **filters: Additional keyword arguments that will be passed as filters to the repository.

        Returns:
            - Generic[Schema]: Paginated results that conform to the provided response schema.
        """
        return await self.task_repository.get_paginated(
            paginator=paginator,
            query_params=query_params,
            response_schema=response_schema,
            **filters
        )

    async def update(self, id: str, **kwargs) -> Task:
        """
        Update a task instance.

        Args:
            - id (str): Task id to update.
            - **kwargs: Fields to update.

        Returns:
            - Task: The updated task instance.
        """
        return await self.task_repository.update(id=id, **kwargs)

    async def increment_retry_count(self, id: str, increment_by: int = 1) -> Task:
        """
        Increment the retry count of a task instance.

        Args:
            - id (str): Task id to update.
            - increment_by (int): The amount to increment the retry count by.

        Returns:
            - Task: The updated task instance.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        return await self.task_repository.increment_retry_count(id=id, increment_by=increment_by)

    async def delete(self, id: str) -> None:
        """
        Delete a task instance.

        Aegs:
            - id (str): Task id to delete.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        await self.task_repository.delete(id=id)


def get_task_service(task_repository: TaskModelRepository = Depends(get_task_repository)) -> TaskService:
    """
    Dependency to get the TaskService instance.

    Args:
        - task_repository (TaskModelRepository): The task repository.

    Returns:
        - TaskService: The TaskService instance.
    """
    return TaskService(
        task_repository=task_repository
    )
