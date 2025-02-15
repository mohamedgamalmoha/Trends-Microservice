from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session

from db import get_db
from models import User


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
