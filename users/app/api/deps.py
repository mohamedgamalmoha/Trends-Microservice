from functools import partial

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from shared_utils import messages
from shared_utils.db.session import get_db

from app.core.conf import settings
from app.core.security import oauth2_scheme, create_token, decode_token, verify_password
from app.models.user import User
from app.repositories.user import get_user_by_email
from app.exceptions import InvalidTokenError, TokenExpiredError


create_access_token = partial(
    create_token,
    expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    key=settings.ACCESS_TOKEN_SECRET_KEY,
    algorithm=settings.ACCESS_TOKEN_ALGORITHM
)

decode_access_token = partial(
    decode_token,
    key=settings.ACCESS_TOKEN_SECRET_KEY,
    algorithm=settings.ACCESS_TOKEN_ALGORITHM
)

create_email_verification_token = partial(
    create_token,
    expires_minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES,
    key=settings.VERIFICATION_TOKEN_SECRET_KEY,
    algorithm=settings.VERIFICATION_TOKEN_ALGORITHM
)

decode_email_verification_token = partial(
    decode_token,
    key=settings.VERIFICATION_TOKEN_SECRET_KEY,
    algorithm=settings.VERIFICATION_TOKEN_ALGORITHM
)

create_password_reset_token = partial(
    create_token,
    expires_minutes=settings.PASSWORD_REST_TOKEN_EXPIRE_MINUTES,
    key=settings.PASSWORD_REST_TOKEN_SECRET_KEY,
    algorithm=settings.PASSWORD_REST_TOKEN_ALGORITHM
)

decode_password_reset_token = partial(
    decode_token,
    key=settings.PASSWORD_REST_TOKEN_SECRET_KEY,
    algorithm=settings.PASSWORD_REST_TOKEN_ALGORITHM
)


async def authenticate_user(email: str, password: str, db: AsyncSession = Depends(get_db)) -> User | None:
    user = await get_user_by_email(email=email, db=db)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
        user = await get_user_by_email(email=payload["email"], db=db)
        if not user:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_MESSAGE
        )
    except (TokenExpiredError, InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_MESSAGE
        )
    else:
        return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )
    return current_user
