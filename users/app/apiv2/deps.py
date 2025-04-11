from fastapi import Depends, HTTPException, status
from shared_utils import messages
from shared_utils.exceptions import ObjDoesNotExist

from app.core.security import oauth2_scheme
from app.models.user import User
from app.exceptions import InvalidTokenError, TokenExpiredError
from app.services.auth import AuthService, get_auth_service


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)
    ) -> User:

    try:
        user = await auth_service.get_auth_user(token=token)
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_MESSAGE
        )
    else:
        return user


async def get_current_admin_user(
        current_user: User = Depends(get_current_user)
    ) -> User:

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    return current_user
