from typing import Sequence, Dict, Any

from fastapi import Depends

from app.models.user import User
from app.repositories.base import UserModelRepository, get_user_repository


class UserService:
    """
    Service class for managing user-related operations.

    This class provides asynchronous methods to create, retrieve, update, and delete user records.
    It interacts with a user repository to perform database operations.
    """

    def __init__(self, user_repository: UserModelRepository) -> None:
        """
        Initialize the UserService with a user repository.

        Args:
            - user_repository (UserModelRepository): The repository used to interact with user data.
        """
        self.user_repository = user_repository

    async def create(self, username: str, email: str, password: str, **other_data: Dict[str, Any]) -> User:
        """
        Create a new user if they do not already exist.

        Args:
            - username (str): The username of the user to create.
            - email (str): The email address of the user to create.
            - password (str): The password of the user to create.
            - **other_data (Dict[str, Any]): other data required to create a new user.

        Returns:
            - User: The created user object.

        Raises:
            - ObjAlreadyExist: If a user with the same username or email already exists.
        """
        user_db = await self.user_repository.create(
            username=username,
            email=email,
            hashed_password=password,
            **other_data
        )
        return user_db

    async def get_by_id(self, id: int) -> User:
        """
        Retrieve a user by their unique ID.

        Args:
            - id (int): The ID of the user to retrieve.

        Returns:
            - User: The user object corresponding to the given ID.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        return await self.user_repository.get_by_id(id=id)

    async def get_by_email(self, email: str) -> User:
        """
        Retrieve a user by their email address.

        Args:
            - email (str): The email address of the user to retrieve.

        Returns:
            - User: The user object corresponding to the given email.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given email.
        """
        return await self.user_repository.get_by_email(email=email)

    async def get_by_username(self, username: str) -> User:
        """
        Retrieve a user by their username.

        Args:
            - username (str): The username of the user to retrieve.

        Returns:
            - User: The user object corresponding to the given username.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given username.
        """
        return await self.user_repository.get_by_username(username=username)

    async def get_all(self) -> Sequence[User]:
        """
        Retrieve all users from the repository.

        Returns:
            - Sequence[User]: A list of all user objects.
        """
        return await self.user_repository.get_all()

    async def update(self, id: int, **update_data: Dict[str, Any]) -> User:
        """
        Update an existing user's information.

        Args:
            - id (int): The ID of the user to update.
            - **user_data (Dict[str, Any]): The new data for the user.

        Returns:
            - User: The updated user object.

        Raises:
            - AssertionError: If password field name is passed within `update_data`.
        """
        return await self.user_repository.update(
            id=id,
            **update_data
        )

    async def set_password(self, id: int, new_password: str) -> None:
        """
        Set a new password for the user.

        Args:
            - id (int): ID of the user.
            - new_password (str): New plain-text password to be hashed and stored.
        """
        await self.user_repository.set_password(id=id, new_password=new_password)

    async def delete(self, id: int) -> None:
        """
        Delete a user by their unique ID.

        Args:
            - id (int): The ID of the user to delete.
        """
        await self.user_repository.delete(id=id)


def get_user_service(user_repository: UserModelRepository = Depends(get_user_repository)) -> UserService:
    """
    Dependency injection provider for UserService.

    Args:
        - user_repository (UserModelRepository, optional): Repository to be used by the service.
          Defaults to result of `get_user_repository`.

    Returns:
        - UserService: An instance of UserService initialized with the provided repository.
    """
    return UserService(
        user_repository=user_repository
    )
