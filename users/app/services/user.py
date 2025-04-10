from typing import Sequence

from fastapi import Depends
from shared_utils.exceptions import ObjAlreadyExist

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
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

    async def create(self, user_data: UserCreate) -> User:
        """
        Create a new user if they do not already exist.

        Args:
            - user_data (UserCreate): Data required to create a new user.

        Returns:
            - User: The created user object.

        Raises:
            - ObjAlreadyExist: If a user with the same username or email already exists.
        """
        is_user_exist = await self.user_repository.is_exist(
            username=user_data.username,
            email=user_data.email
        )
        if is_user_exist:
            raise ObjAlreadyExist

        user_db_data = user_data.model_dump(exclude=['password', 'password_confirm'])
        user_db = await self.user_repository.create(
            **user_db_data,
            hashed_password=user_data.password
        )

        return user_db

    async def get_by_id(self, id: int) -> User:
        """
        Retrieve a user by their unique ID.

        Args:
            id (int): The ID of the user to retrieve.

        Returns:
            User: The user object corresponding to the given ID.
        """
        return await self.user_repository.get_by_id(id=id)

    async def get_by_email(self, email: str) -> User:
        """
        Retrieve a user by their email address.

        Args:
            - email (str): The email address of the user to retrieve.

        Returns:
            - User: The user object corresponding to the given email.
        """
        return await self.user_repository.get_by_email(email=email)

    async def get_by_username(self, username: str) -> User:
        """
        Retrieve a user by their username.

        Args:
            - username (str): The username of the user to retrieve.

        Returns:
            - User: The user object corresponding to the given username.
        """
        return await self.user_repository.get_by_username(username=username)

    async def get_all(self) -> Sequence[User]:
        """
        Retrieve all users from the repository.

        Returns:
            - Sequence[User]: A list of all user objects.
        """
        return await self.user_repository.get_all()

    async def delete(self, id: int) -> None:
        """
        Delete a user by their unique ID.

        Args:
            - id (int): The ID of the user to delete.
        """
        await self.user_repository.delete(id=id)

    async def update(self, id: int, user_data: UserUpdate) -> User:
        """
        Update an existing user's information.

        Args:
            - id (int): The ID of the user to update.
            - user_data (UserUpdate): The new data for the user.

        Returns:
            - User: The updated user object.
        """
        user_db_data = user_data.model_dump()
        return await self.user_repository.update(
            id=id,
            **user_db_data
        )


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
