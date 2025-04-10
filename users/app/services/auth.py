from fastapi import Depends

from app.core.security import verify_password, create_access_token, decode_access_token
from app.models.user import User
from app.services.user import UserService, get_user_service
from app.exceptions import InvalidUserCredentials


class AuthService:
    """
    Service class for handling user authentication and authorization.

    Provides methods for authenticating users, generating access tokens,
    and verifying token and password validity.
    """

    def __init__(self, user_service: UserService) -> None:
        """
        Initialize the AuthService with a UserService instance.

        Args:
            - user_service (UserService): The user service used to retrieve user data.
        """
        self.user_service = user_service

    async def create_auth_token(self, email: str, password: str) -> str:
        """
        Authenticate the user and generate an access token.

        Args:
            - email (str): The user's email.
            - password (str): The user's  password input.

        Returns:
            - token (str): A JWT access token for the authenticated user.

        Raises:
            - InvalidUserCredentials: If the user's credentials are invalid.
        """
        user_data = await self.authenticate(
            email=email,
            password=password
        )
        return create_access_token(email=user_data.email)

    async def get_auth_user(self, token: str) -> User:
        """
        Retrieve the authenticated user from a JWT token.

        Args:
            - token (str): A JWT access token.

        Returns:
            - User: The authenticated user associated with the token.
        """
        payload = decode_access_token(token)
        user_db = await self.user_service.get_by_email(email=payload['email'])
        return user_db

    async def authenticate(self, email: str, password: str) -> User:
        """
        Authenticate a user based on email and password.

        Args:
            - email (str): The user's email.
            - password (str): The user's raw password input.

        Returns:
            - User: The authenticated user object.

        Raises:
            - InvalidUserCredentials: If the credentials are incorrect.
        """
        user_db = await self.user_service.get_user_by_email(email=email)
        if not verify_password(plain_password=password, hashed_password=user_db.hased_password):
            raise InvalidUserCredentials()
        return user_db


def get_auth_service(user_service: UserService = Depends(get_user_service)) -> AuthService:
    """
    Dependency injection provider for AuthService.

    Args:
        - user_service (UserService, optional): User service used for authentication logic.
          Defaults to result of `get_user_service`.

    Returns:
        - AuthService: An instance of AuthService.
    """
    return AuthService(
        user_service=user_service
    )
