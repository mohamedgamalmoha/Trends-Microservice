from typing import List, Type

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists, or_

from db import get_db
from models import User


def is_user_exist(email: str, username: str, db: Session = Depends(get_db)) -> bool:
    return db.query(
        exists().where(
            or_(
                User.email == email,
                User.username == username
            )
        )
    ).scalar()


def get_user_by_id(id: int, db: Session = Depends(get_db)) -> Type[User] | None:
    return db.query(User).filter_by(id=id, is_active=True).first()


def get_user_by_email(email: str, db: Session = Depends(get_db)) -> Type[User] | None:
    return db.query(User).filter_by(email=email, is_active=True).first()


def get_user_by_username(username: str, db: Session = Depends(get_db))-> Type[User] | None:
    return db.query(User).filter_by(username=username, is_active=True).first()


def get_all_users(db: Session = Depends(get_db)) -> List[Type[User]]:
    return db.query(User).all()


def get_active_users(db: Session = Depends(get_db)) -> List[Type[User]]:
    return db.query(User).filter_by(is_active=True).all()


def get_admin_users(db: Session = Depends(get_db)) -> List[Type[User]]:
    return db.query(User).filter_by(is_admin=True).all()


def get_non_admin_users(db: Session = Depends(get_db)) -> List[Type[User]]:
    return db.query(User).filter_by(is_admin=False).all()
