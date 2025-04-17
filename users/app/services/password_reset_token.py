from app.core.security import create_password_reset_token, decode_password_reset_token


class PasswordResetTokenService:
    """
    A service class for handling password reset token operations.

    This class provides an interface to create and decode password reset tokens,
    typically implemented as time-limited JWTs. It abstracts the underlying token
    logic to improve modularity, reusability, and testability.
    """

    def create(self, email: str) -> str:
        """
        Create a new password reset token for the given user email.

        Args:
            - email (str): The email address of the user requesting a password reset.

        Returns:
            - str: A time-limited JWT password reset token.
        """
        return create_password_reset_token(email=email)

    def decode(self, token: str) -> dict:
        """
        Decode a password reset token and return its payload.

        This method validates the token, ensuring it hasn't expired and
        that it's properly formed. It extracts useful information, like the
        user's email, from the token payload.

        Args:
            - token (str): The JWT password reset token to decode.

        Returns:
            - dict: The decoded token payload containing user information.

        Raises:
            - TokenExpiredError: If the token has expired.
            - InvalidTokenError: If the token is malformed or invalid.
        """
        return decode_password_reset_token(token)


def get_password_reset_token_service() -> PasswordResetTokenService:
    """
    Dependency injection provider for the PasswordResetTokenService.

    Returns:
        - PasswordResetTokenService: An instance of PasswordResetTokenService.
    """
    return PasswordResetTokenService()
