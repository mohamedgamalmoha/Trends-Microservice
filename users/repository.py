from typing import Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import User
from auth import hash_password
from query import get_user_by_id
from schema import UserCreate, AdminUserCreate, UserUpdate


async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        hashed_password=hash_password(user.password)
    )

    async with db.begin():
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

    return db_user


async def create_admin_user(user: AdminUserCreate, db: AsyncSession = Depends(get_db)) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        ia_active=True,
        ia_admin=True,
        hashed_password=hash_password(user.password)
    )

    async with db.begin():
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

    return db_user


async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)) -> Type[User] | None:
    db_user = await get_user_by_id(user_id, db)

    if not db_user:
        return None

    if user.first_name and db_user.first_name != user.first_name:
        db_user.first_name = user.first_name

    if user.last_name and db_user.last_name != user.last_name:
        db_user.last_name = user.last_name

    if user.phone_number and db_user.phone_number != user.phone_number:
        db_user.phone_number = user.phone_number

    async with db.begin():
        await db.commit()
        await db.refresh(db_user)

    return db_user


async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    db_user = await get_user_by_id(user_id, db)

    if not db_user:
        return None

    async with db.begin():
        await db.delete(db_user)
        await db.commit()
