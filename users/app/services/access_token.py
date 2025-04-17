from app.core.security import create_access_token, decode_access_token


class AccessTokenService:
    """
    A service class responsible for managing access tokens.

    This class encapsulates the logic for creating and decoding
    JSON Web Tokens (JWT) used for authenticating users in a secure manner.
    """

    def create(self, email: str) -> str:
        """
        Create a new JWT access token for a given user email.

        This token can be used to authenticate the user in subsequent
        requests. The email is embedded into the token payload.

        Args:
            - email (str):The user's email address to encode in the token.

        Returns:
            - str: A JWT access token as a string.
        """
        return create_access_token(email=email)

    def decode(self, token: str) -> dict:
        """
        Decode a JWT access token and return its payload.

        This method verifies the token's signature and expiration,
        and extracts the payload data, typically including the user's email.

        Args:
            - token (str): The JWT token string to decode.

        Returns:
            - dict: The decoded token payload, typically containing user information.

        Raises:
            - TokenExpiredError: If the token has expired.
            - InvalidTokenError: If the token is malformed or invalid.
        """
        return decode_access_token(token)


def get_access_token_service() -> AccessTokenService:
    """
    Dependency injection provider for the AccessTokenService.

    Returns:
        - AccessTokenService: An instance of AccessTokenService.
    """
    return AccessTokenService()
