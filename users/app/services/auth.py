from fastapi import Depends

from app.models.user import User
from app.exceptions import InvalidUserCredentials, InvalidTokenError
from app.services.user import UserService, get_user_service
from app.services.password import PasswordService, get_password_service
from app.services.access_token import AccessTokenService, get_access_token_service


class AuthService:
    """
    A service class responsible for handling user authentication.

    Supports both basic authentication (email and password) and
    token-based authentication using JSON Web Tokens (JWT).
    """

    def __init__(
            self,
            user_service: UserService,
            password_service: PasswordService,
            token_service: AccessTokenService
    ) -> None:
        """
        Initialize the AuthService with its dependencies.

        Args:
            - user_service (UserService): Service for accessing user data.
            - password_service (PasswordService): Service for verifying user passwords.
            - token_service (TokenService): Service for creating and decoding access tokens.
        """
        self.user_service = user_service
        self.password_service = password_service
        self.token_service = token_service

    async def authenticate_basic(self, email: str, password: str) -> User:
        """
        Authenticate a user using basic authentication (email and password).

        Args:
            - email (str): The user's email address.
            - password (str): The user's plain-text password.

        Returns:
            - User: The authenticated user object.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given email.
            - InvalidUserCredentials: If authentication fails due to invalid credentials.
        """
        user = await self.user_service.get_by_email(email=email)

        if not self.password_service.verify_password(password, user.hashed_password):
            raise InvalidUserCredentials()

        return user

    async def authenticate_token(self, token: str) -> User:
        """
        Authenticate a user using a JWT access token.

        Args:
            - token (str): The JWT token containing the user's identity.

        Returns:
            - User: The authenticated user object.

        Raises:
            - InvalidTokenError: If the token is malformed or invalid.
            - TokenExpiredError: If the token has expired.
            - ObjDoesNotExist: If no instance is found with the given email.
        """
        payload = self.token_service.decode(token)

        if 'email' not in payload:
            raise InvalidTokenError()

        return await self.user_service.get_by_email(email=payload['token'])


def get_auth_service(
        user_service: UserService = Depends(get_user_service),
        password_service: PasswordService = Depends(get_password_service),
        token_service: AccessTokenService = Depends(get_access_token_service)
    ) -> AuthService:
    """
    Dependency injection provider for the AuthService.

    Args:
        - user_service (UserService, optional): Service for accessing user data.
        - password_service (PasswordService, optional): Service for verifying user passwords.
        - token_service (TokenService, optional): Service for creating and decoding access tokens.

    Returns:
        - AuthService: An instance of AuthService.
    """
    return AuthService(
        user_service=user_service,
        password_service=password_service,
        token_service=token_service
    )
