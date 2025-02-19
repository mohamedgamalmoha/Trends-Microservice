from typing import Type

from fastapi import Depends
from sqlalchemy.orm import Session

from db import get_db
from models import User
from auth import hash_password
from query import get_user_by_id
from schema import UserCreate, UserUpdate


def create_user(user: UserCreate, db: Session = Depends(get_db)) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        hashed_password=hash_password(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)) -> Type[User] | None:
    db_user = get_user_by_id(user_id)

    if user.first_name and db_user.first_name != user.first_name:
        db_user.first_name = user.first_name

    if user.last_name and db_user.last_name != user.last_name:
        db_user.last_name = user.last_name

    if user.phone_number and db_user.phone_number != user.phone_number:
        db_user.phone_number = user.phone_number

    db.commit()
    db.refresh(db_user)

    return db_user


def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    db_user = get_user_by_id(user_id)
    db.delete(db_user)
    db.commit()
