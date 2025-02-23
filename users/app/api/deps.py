from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app import messages
from app.db import get_db
from app.models.user import User
from app.repositories.user import get_user_by_email
from app.core.security import oauth2_scheme, decode_access_token, verify_password
from app.exceptions import InvalidTokenError, TokenExpiredError


async def authenticate_user(email: str, password: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(email=email, db=db)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Type[User]:
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
