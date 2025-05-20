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
    async def create(self, id: str, user_id: str, q: str, **other_fields) -> Task:
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
        try:
            await self.get_by_id(id=id)
        except ObjDoesNotExist:
            return await super().create(id=id, user_id=user_id, q=q, **other_fields)
        
        raise ObjDoesNotExist

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
        await self.filter_by(id=id, user_id=user_id)

    async def update(self, id: str, **kwargs) -> Task:
        """
        Update a task instance.

        Args:
            - id (str): Task id to update.
            - **kwargs: Fields to update.

        Returns:
            - Task: The updated task instance.
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
        task = self.get_by_id(id=id)
        increment_count = task.retry_count + increment_by
        return await self.update(id=id, retry_count=increment_count)

    async def delete(self, id: str) -> None:
        """
        Delete a task instance.

        Aegs:
            - id (str): Task id to delete.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        await super().delete(id=id)


def get_task_repository(db: AsyncSession = Depends(get_db)) -> TaskModelRepository:
    """
    Dependency to get the TaskModelRepository instance.

    Args:
        - db (AsyncSession): The database session.

    Returns:
        - TaskModelRepository: The TaskModelRepository instance.
    """
    return TaskModelRepository(
        db=db
    )
