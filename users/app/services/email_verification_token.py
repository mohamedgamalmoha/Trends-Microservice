from app.core.security import create_email_verification_token, decode_email_verification_token


class EmailVerificationTokenService:
    """
    A service class for handling email verification token operations.

    This class provides methods to generate and decode email verification tokens,
    which are typically used to confirm a user's email address during registration
    or email change workflows. Tokens are usually time-limited and encoded as JWTs.
    """

    def create(self, email: str) -> str:
        """
        Create a new email verification token for the given user email.

        Args:
            - email (str): The email address to include in the token for verification.

        Returns:
            - str: A time-limited JWT email verification token.
        """
        return create_email_verification_token(email=email)

    def decode(self, token: str) -> dict:
        """
        Decode an email verification token and return its payload.

        This method ensures the token is valid, has not expired, and returns the
        embedded information (typically including the email).

        Args:
            - token (str): The JWT email verification token to decode.

        Returns:
            - dict: The decoded payload containing the email and other metadata.

        Raises:
            - TokenExpiredError: If the token has expired.
            - InvalidTokenError: If the token is malformed or invalid.
        """
        return decode_email_verification_token(token)


def get_email_verification_token_service() -> EmailVerificationTokenService:
    """
    Dependency injection provider for the EmailVerificationTokenService.

    Returns:
        - EmailVerificationTokenService: An instance of EmailVerificationTokenService.
    """
    return EmailVerificationTokenService()
