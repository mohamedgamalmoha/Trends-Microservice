from typing import Sequence, Optional

from fastapi import Depends
from sqlalchemy.sql import select, exists, or_
from sqlalchemy.ext.asyncio import AsyncSession
from shared_utils.db.session import get_db
from shared_utils.exceptions import ObjDoesNotExist, ObjAlreadyExist
from shared_utils.repository.sqlalchemy import SQLAlchemyModelRepository

from app.models.user import User
from app.core.security import hash_password


class UserModelRepository(SQLAlchemyModelRepository[User]):
    """
    Repository class for interacting with the `User` model using SQLAlchemy.

    This class provides methods for creating, updating, and retrieving user records,
    including functionality for setting passwords, checking user existence, and 
    retrieving admin or active users.
    """

    async def create(self, email: str, username: str, password: str, **other_fields) -> User:
        """
        Create a new user with a hashed password.

        Args:
            - email(str): User`s email to create.
            - username(str): User`s username to create.
            - password: User`s password to create.
            - **other_fields: Remaining fields to create.

        Returns:
            - User: The created user instance.

        Raises:
            - ObjAlreadyExist: If a user with the same username or email already exists.
        """
        is_user_exist = await self.is_exist(
            username=username,
            email=email
        )
        if is_user_exist:
            raise ObjAlreadyExist()

        hashed_password = hash_password(password=password)

        return await super().create(email=email, username=username, hashed_password=hashed_password, **other_fields)

    async def create_admin(self, email: str, username: str, password: str, **other_fields) -> User:
        """
        Create a new admin user. Defaults to `is_active=True` and `is_admin=True`.

        Args:
            - email(str): Admin`s email to create.
            - username(str): Admin`s username to create.
            - password: Admin`s password to create.
            - **other_fields: Fields to create.

        Returns:
            - User: The created admin user instance.

        Raises:
            - ObjAlreadyExist: If a user with the same username or email already exists.
        """
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_admin', True)


        return await self.create(email=email, username=username, password=password, **other_fields)

    async def is_exist(self, email: str, username: str) -> bool:
        """
        Check if a user exists with the given email or username.

        Args:
            - email (str): Email to check.
            - username (str): Username to check.

        Returns:
            - bool: True if user exists, False otherwise.
        """
        result = await self.db.execute(
            select(
                exists().where(
                    or_(
                        self.model_class.email == email,
                        self.model_class.username == username
                    )
                )
            )
        )
        return result.scalar()

    async def get_by_email(self, email: str) -> User:
        """
        Retrieve an active user by email.

        Args:
            - email (str): The email of the user.

        Returns:
            - User: The matched user instance.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given email.
        """
        result = await self.get_by(
            email=email,
            is_active=True
        )

        if not result:
            raise ObjDoesNotExist

        return result

    async def get_by_username(self, username: str) -> User:
        """
        Retrieve an active user by username.

        Args:
            - username (str): The username of the user.

        Returns:
            - User: The matched user instance.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given username.
        """
        result = await self.get_by(
            username=username,
            is_active=True
        )

        if not result:
            raise ObjDoesNotExist

        return result

    async def get_active(self) -> Optional[Sequence[User]]:
        """
        Retrieve all active users.

        Returns:
            - Optional[Sequence[User]]: A list of active users or None.
        """
        return await self.filter_by(
            is_actvie=True
        )

    async def get_admin(self) -> Optional[Sequence[User]]:
        """
        Retrieve all admin users.

        Returns:
            - Optional[Sequence[User]]: A list of admin users or None.
        """
        return await self.filter_by(
            is_admin=True
        )

    async def get_none_admin(self) -> Optional[Sequence[User]]:
        """
        Retrieve all non-admin users.

        Returns:
            - Optional[Sequence[User]]: A list of non-admin users or None.
        """
        return await self.filter_by(
            is_admin=False
        )

    async def update(self, id: int, **fields) -> User:
        """
        Update user details. Does not allow password update through this method.

        Args:
            - id (int): ID of the user to update.
            - **fields: Fields to update.

        Returns:
            - User: The updated user instance.

        Raises:
            - ValueError: If password is included in the fields to update.
        """
        if 'password' in fields:
            raise ValueError("Password update is not allowed through this method, use `set_password` instead.")
        return await super().update(id=id, **fields)

    async def set_password(self, id: int, new_password: str) -> None:
        """
        Set a new password for the user.

        Args:
            - id (int): ID of the user.
            - new_password (str): New plain-text password to be hashed and stored.
        """
        obj = await self.get_by_id(id=id)

        hashed_password = hash_password(new_password)

        setattr(obj, 'hashed_password', hashed_password)

        await self.db.commit()
        await self.db.refresh(obj)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserModelRepository:
    """
    Dependency injection function to provide a UserModelRepository instance.

    Args:
        - db (AsyncSession): The SQLAlchemy async session.

    Returns:
        - UserModelRepository: A repository instance for User model operations.
    """
    return UserModelRepository(
        db=db
    )
