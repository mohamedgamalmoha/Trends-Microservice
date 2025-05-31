from typing import Sequence

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from shared_utils.db.session import get_db
from shared_utils.exceptions import ObjDoesNotExist
from shared_utils.repository.sqlalchemy import SQLAlchemyModelRepository

from app.models.task import Task


class TaskModelRepository(SQLAlchemyModelRepository[Task]):
    """
    TaskModelRepository is a repository class for managing Task instances.
    It provides methods to create, retrieve, update, and delete Task records
    in the database using SQLAlchemy ORM.
    """

    async def create(self, id: str, user_id: str, search_task_id: str, **other_fields) -> Task:
        """
        Create a new task instance.

        Args:
            - id (str): Task id to create.
            - user_id (str): User id to associate with the task.
            - search_task_id (str): Search task id to associate with the task.
            - **other_fields: Other fields to set on the task instance.

        Returns:
            - Task: The created task instance.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        return await super().create(id=id, user_id=user_id, search_task_id=search_task_id, **other_fields)

    async def filter_by_user_id(self, user_id: str) -> Sequence[Task]:
        """
        Get all tasks by user id.

        Args:
            - user_id (str): User id to search for.

        Returns:
            - List[Task]: List of task instances associated with the user id.
        """
        return await self.filter_by(user_id=user_id)

    async def get_by_id(self, id: str) -> Task:
        """
        Get task by task id & user id.

        Args:
            - id (str): Task id to search for.

        Returns:
            - Task: The task instance if found.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        return await super().get_by_id(id=id)

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
        results = await self.filter_by(id=id, user_id=user_id)
        
        if not results:
            raise ObjDoesNotExist
        
        return results[0]

    async def get_by_search_task_id(self, id: str, search_task_id: str) -> Task:
        """
        Get task by task id & search task id.

        Args:
            - id (str): Task id to search for.
            - search_task_id (str): Search task id to search for.

        Returns:
            - Task: The task instance if found.
        """
        return await self.filter_by(id=id, search_task_id=search_task_id)

    async def get_by_user_id_and_search_task_id(self, id: str, user_id: str, search_task_id: str) -> Task:
        """
        Get task by task id & user id & search task id.

        Args:
            - id (str): Task id to search for.
            - user_id (str): User id to search for.
            - search_task_id (str): Search task id to search for.

        Returns:
            - Task: The task instance if found.
        """
        return await self.filter_by(id=id, user_id=user_id, search_task_id=search_task_id)

    async def update(self, id: str, **kwargs) -> Task:
        """
        Update a task instance.

        Args:
            - id (str): Task id to update.
            - **kwargs: Fields to update on the task instance.

        Returns:
            - Task: The updated task instance.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        return await super().update(id=id, **kwargs)

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
        task = await self.get_by_id(id=id)
        increment_count = task.retry_count + increment_by
        return await self.update(id=id, retry_count=increment_count)

    async def delete(self, id: str) -> None:
        """
        Delete a task instance.

        Args:
            - id (str): Task id to delete.

        Returns:
            - None

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        return await super().delete(id=id)


def get_task_repository(db: AsyncSession = Depends(get_db)) -> TaskModelRepository:
    """
    Dependency to get the TaskModelRepository instance.

    Args:
        - db (AsyncSession): The database session to use.

    Returns:
        - TaskModelRepository: The task repository instance.
    """
    return TaskModelRepository(
        db=db
    )
