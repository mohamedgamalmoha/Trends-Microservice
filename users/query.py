from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session

from db import get_db
from models import User
from auth import hash_password
from schema import UserCreate, UserUpdate


async def is_user_exist(username: str, email: str, db: Session = Depends(get_db)) -> User:
    return db.query(User).filter(User.username == username or User.email == email).first()


async def get_user_by_id(id: int, db: Session = Depends(get_db)) -> User:
    return db.query(User).filter(User.id == id and User.is_verified==True).first()


async def get_user_by_email(email: str, db: Session = Depends(get_db)) -> User:
    return db.query(User).filter(User.email == email and User.is_verified==True).first()


async def get_user_by_username(username: str, db: Session = Depends(get_db)) -> User:
    return db.query(User).filter(User.username == username and User.is_verified==True).first()


async def get_all_users(db: Session = Depends(get_db)) -> List[User]:
    return db.query(User).all()


async def get_active_users(db: Session = Depends(get_db)) -> List[User]:
    return db.query(User).filter(User.is_active == True)


async def get_admin_users(db: Session = Depends(get_db)) -> List[User]:
    return db.query(User).filter(User.is_admin == True)


async def get_non_admin_users(db: Session = Depends(get_db)) -> List[User]:
    return db.query(User).filter(User.is_admin == False)


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


async def update_user(email: str, user: UserUpdate, db: Session = Depends(get_db)) -> User:
    db_user = await get_user_by_email(email)

    if user.first_name and db_user.first_name != user.first_name:
        db_user.first_name = user.first_name

    if user.last_name and db_user.last_name != user.last_name:
        db_user.last_name = user.last_name

    if user.phone_number and db_user.phone_number != user.phone_number:
        db_user.phone_number = user.phone_number

    db.commit()
    db.refresh(db_user)

    return db_user


async def delete_user(email: str, db: Session = Depends(get_db)) -> None:
    db_user = await get_user_by_email(email)
    db.delete(db_user)
    db.commit()
