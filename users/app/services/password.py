from app.core.security import verify_password


class PasswordService:
    """
    A service class responsible for handling password-related operations.

    This class provides an abstraction over low-level password utilities,
    such as verifying a plain-text password against its hashed version.
    It helps encapsulate authentication logic and can be easily extended or
    replaced for testing or customization purposes.
    """

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify whether the provided plain-text password matches the hashed password.

        Args:
        - plain_password (str): The plain-text password input provided by the user.
        - hashed_password (str): The hashed version of the password stored in the database.

        Returns:
            - bool: Returns True if the plain-text password matches the hashed version; otherwise, returns False.
        """
        return verify_password(
            plain_password=plain_password,
            hashed_password=hashed_password
        )


def get_password_service() -> PasswordService:
    """
    Dependency injection provider for the PasswordService.

    Returns:
        - PasswordService: An instance of PasswordService.
    """
    return PasswordService()
