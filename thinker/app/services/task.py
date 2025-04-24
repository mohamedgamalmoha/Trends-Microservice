from typing import Sequence

from fastapi import Depends

from app.models.task import Task
from app.repositories.task import TaskRepository, get_task_repository


class TaskService:
    """
    Service class for managing task-related operations.
    This class provides asynchronous methods to create, retrieve, update, and delete task records.
    It interacts with a task repository to perform database operations.
    """

    def __init__(self, task_repository: TaskRepository) -> None:
        """
        Initialize the TaskService with a task repository.

        Args:
            - task_repository (TaskRepository): The repository used to interact with task data.
        """
        self.task_repository = task_repository

    async def create(self, id: str, user_id: str, q: str, **other_fields)  -> Task:
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

    async def get_by_search_task_id(self, id: str, search_task_id: str) -> Task:
        """
        Get task by task id & search task id.

        Args:
            - id (str): Task id to search for.
            - search_task_id (str): Search task id to search for.

        Returns:
            - Task: The task instance if found.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        return await self.task_repository.get_by_search_task_id(id=id, search_task_id=search_task_id)

    async def get_by_user_id_and_search_task_id(self, id: str, user_id: str, search_task_id: str) -> Task:
        """
        Get task by task id & user id & search task id.
        Args:
            - id (str): Task id to search for.
            - user_id (str): User id to search for.
            - search_task_id (str): Search task id to search for.
        Returns:
            - Task: The task instance if found.
        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        return await self.task_repository.get_by_user_id_and_search_task_id(id=id, user_id=user_id, search_task_id=search_task_id)

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


def get_task_service(task_repository: TaskRepository = Depends(get_task_repository)) -> TaskService:
    """
    Dependency to get the TaskService instance.

    Args:
        - task_repository (TaskRepository): The task repository.

    Returns:
        - TaskService: The TaskService instance.
    """
    return TaskService(
        task_repository=task_repository
    )
