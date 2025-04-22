from fastapi import Depends, HTTPException, status
from shared_utils import messages
from shared_utils.exceptions import ObjDoesNotExist

from app.core.security import security
from app.models.user import User
from app.exceptions import InvalidTokenError, TokenExpiredError
from app.services.auth import AuthService, get_auth_service


async def get_current_user(
        token: str = Depends(security),
        auth_service: AuthService = Depends(get_auth_service)
    ) -> User:
    """
    Retrieve the currently authenticated user from a JWT token.

    This function uses the provided token and authentication service to
    validate and decode the token, returning the associated user object.

    Args:
        - token (str): JWT access token, typically passed via Authorization header.
        - auth_service (AuthService): Service used to authenticate the token and fetch user details.

    Returns:
        - User: The authenticated user object.

    Raises:
        - HTTPException:
            - 401 Unauthorized if the token is expired or invalid,
            - if the user is not found,
            - or if an unexpected error occurs during authentication.
    """
    try:
        user = await auth_service.authenticate_token(token=token)
    except (TokenExpiredError, InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
    except ObjDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.USER_NOT_FOUND_MESSAGE
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_MESSAGE
        )
    return user


async def get_current_admin_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
    """
    Ensure the current authenticated user has administrative privileges.

    This function depends on `get_current_user` to retrieve the user, then checks
    if the user has administrative rights.

    Args:
        - current_user (User): The currently authenticated user, provided via dependency injection.

    Returns:
        - User: The authenticated user object with admin rights.

    Raises:
        - HTTPException: 403 Forbidden if the user does not have admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )
    return current_user
