from fastapi import Depends

from app.core.security import create_password_reset_token, decode_password_reset_token
from app.models.user import User
from app.services.user import UserService, get_user_service


class PasswordService:
    """
    A service for handling password reset token operations for users.
    """

    def __init__(self, user_service: UserService) -> None:
        """
        Initialize the PasswordService with a UserService instance.

        Args:
            - user_service (UserService): A service to manage and retrieve user information.
        """
        self.user_service = user_service

    async def create_reset_token(self, email: str) -> str:
        """
        Create a password reset token for a user identified by their email.

        Args:
            - email (str): The email address of the user requesting a password reset.

        Returns:
            - str: A password reset token tied to the user's email.
        """
        db_user = await self.user_service.get_by_email(email=email)
        return create_password_reset_token(email=db_user.email)

    async def decode_reset_token(self, token: str) -> User:
        """
        Decode a password reset token and retrieve the corresponding user.

        Args:
            - token (str): The password reset token to decode.

        Returns:
            - User: The user associated with the decoded token.
        """
        pyload = decode_password_reset_token(token=token)
        user_db = await self.user_service.get_by_email(email=pyload['email'])
        return user_db


def get_password_service(user_service: UserService = Depends(get_user_service)) -> PasswordService:
    """
    Dependency injection provider for PasswordService.

    Args:
        - user_service (UserService, optional): User service used for authentication logic.
          Defaults to result of `get_user_service`.

    Returns:
        - PasswordService: An instance of PasswordService.
    """
    return PasswordService(
        user_service=user_service
    )
