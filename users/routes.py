from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

import messages
from main import app
from db import get_db
from models import User
from auth import authenticate_user, create_access_token, get_current_user
from schema import UserCreate, UserLogin, UserUpdate, UserRetrieve, Token
from repository import create_user, update_user, delete_user
from query import is_user_exist,  get_user_by_id, get_all_users


@app.post('/api/jwt/create/', status_code=status.HTTP_200_OK, response_model=Token)
def create_jwt_route(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(email=user_data.email, password=user_data.password, db=db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_CREDENTIALS_MESSAGE
        )

    access_token = create_access_token(email=user.email)

    return Token(access_token=access_token, token_type='Bearer')


@app.post('/api/users/', status_code=status.HTTP_201_CREATED, response_model=UserRetrieve)
def create_user_route(user_data: UserCreate,  db: Session = Depends(get_db)):
    db_user = is_user_exist(username=user_data.username, email=user_data.email, db=db)

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.USER_ALREADY_EXIST_MESSAGE
        )

    db_user = create_user(user=user_data, db=db)

    return db_user


@app.get('/api/users/{user_id}/', status_code=status.HTTP_200_OK, response_model=UserRetrieve)
def get_user_route(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_id(id=user_id, db=db)
    if user and (current_user.is_admin or current_user.id == user_id):
            return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=messages.USER_NOT_FOUND_MESSAGE
    )


@app.get('/api/users/', status_code=status.HTTP_200_OK, response_model=List[UserRetrieve])
def get_users_route(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = get_all_users(db=db)
    return users


@app.delete('/api/users/{user_id}/', status_code=status.HTTP_204_NO_CONTENT)
def delete_user_route(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_id(id=user_id, db=db)
    if user and (current_user.is_admin or current_user.id == user_id):
        delete_user(user_id=user_id, db=db)
        return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=messages.USER_NOT_FOUND_MESSAGE
    )


@app.put('/api/users/{user_id}/', status_code=status.HTTP_200_OK, response_model=UserRetrieve)
def update_user_route(user_id: int, user_data: UserUpdate, current_user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    return update_user(user_id=user_id, user=user_data, db=db)
