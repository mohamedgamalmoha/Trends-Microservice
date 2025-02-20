from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

import messages
from db import get_db
from models import User
from auth import authenticate_user, create_access_token, get_current_user
from schema import UserCreate, UserLogin, UserUpdate, UserRetrieve, Token
from repository import create_user, update_user, delete_user
from query import is_user_exist,  get_user_by_id, get_all_users


auth_router = APIRouter(
    prefix='/jwt',
    tags = ['auth']
)

user_router = APIRouter(
    prefix='/users',
    tags = ['users']
)


@auth_router.post('/create/', status_code=status.HTTP_200_OK, response_model=Token)
async def create_jwt_route(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(email=user_data.email, password=user_data.password, db=db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_CREDENTIALS_MESSAGE
        )

    access_token = create_access_token(email=user.email)

    return Token(access_token=access_token)


@auth_router.get('/verify/', status_code=status.HTTP_204_NO_CONTENT)
async def verify_jwt_token_route(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ...


@user_router.get('/me/', status_code=status.HTTP_200_OK, response_model=UserRetrieve)
async def get_user_route(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return current_user


@user_router.post('/', status_code=status.HTTP_201_CREATED, response_model=UserRetrieve)
async def create_user_route(user_data: UserCreate,  db: AsyncSession = Depends(get_db)):
    db_user = await is_user_exist(username=user_data.username, email=user_data.email, db=db)

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.USER_ALREADY_EXIST_MESSAGE
        )

    db_user = await create_user(user=user_data, db=db)

    return db_user


@user_router.get('/{user_id}/', status_code=status.HTTP_200_OK, response_model=UserRetrieve)
async def get_user_route(user_id: int, current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(id=user_id, db=db)

    if user:
        if current_user.is_admin or current_user.id == user_id:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=messages.USER_FORBIDDEN_MESSAGE
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=messages.USER_NOT_FOUND_MESSAGE
    )


@user_router.get('/', status_code=status.HTTP_200_OK, response_model=List[UserRetrieve])
async def get_users_route(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

    if current_user.is_admin:
        users = get_all_users(db=db)
        return users

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=messages.USER_FORBIDDEN_MESSAGE
    )


@user_router.delete('/{user_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(user_id: int, current_user: User = Depends(get_current_user),
                            db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(id=user_id, db=db)

    if user:
        if current_user.is_admin or current_user.id == user_id:
            await delete_user(user_id=user_id, db=db)
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=messages.USER_FORBIDDEN_MESSAGE
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=messages.USER_NOT_FOUND_MESSAGE
    )


@user_router.put('/{user_id}/', status_code=status.HTTP_200_OK, response_model=UserRetrieve)
async def update_user_route(user_id: int, user_data: UserUpdate, current_user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(id=user_id, db=db)

    if user:
        if current_user.is_admin or current_user.id == user_id:
            return await update_user(user_id=user_id, user=user_data, db=db)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=messages.USER_FORBIDDEN_MESSAGE
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=messages.USER_NOT_FOUND_MESSAGE
    )
