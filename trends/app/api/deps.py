from typing import Annotated

import aiohttp
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app import messages
from app.core.conf import settings
from app.core.security import security
from app.schemas.user import User


async def get_current_user(token: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> User:

    async with aiohttp.ClientSession() as session:
        async with session.get(
                url=settings.USER_AUTH_URL,
                headers={'Authorization': f'{token.scheme} {token.credentials}'}
        ) as response:

            if response.status != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=messages.INVALID_TOKEN_MESSAGE
                )

            return User(
                ** await response.json()
            )


async def get_current_admin_user(current_user = Depends(get_current_user)) -> User:

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    return current_user
