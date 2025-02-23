from typing import Type, Sequence

from fastapi import Depends
from sqlalchemy.sql import select, exists, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserUpdate, _AdminUserCreate


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


async def _create_admin_user(user: _AdminUserCreate, db: AsyncSession = Depends(get_db)) -> User:
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


async def is_user_exist(email: str, username: str, db: AsyncSession = Depends(get_db)) -> bool:
    result = await db.execute(
        select(
            exists().where(
                or_(
                    User.email == email,
                    User.username == username
                )
            )
        )
    )
    return result.scalar()


async def get_user_by_id(id: int, db: AsyncSession = Depends(get_db)) -> Type[User] | None:
    result = await db.execute(
        select(User).filter_by(id=id, is_active=True)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)) -> Type[User] | None:
    result = await db.execute(
        select(User).filter_by(email=email, is_active=True)
    )
    return result.scalar_one_or_none()


async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)) -> Type[User] | None:
    result = await db.execute(
        select(User).filter_by(username=username, is_active=True)
    )
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession = Depends(get_db)) -> Sequence[User]:
    result = await db.execute(select(User))
    return result.scalars().all()


async def get_active_users(db: AsyncSession = Depends(get_db)) -> Sequence[User]:
    result = await db.execute(
        select(User).filter_by(is_active=True)
    )
    return result.scalars().all()


async def get_admin_users(db: AsyncSession = Depends(get_db)) -> Sequence[User]:
    result = await db.execute(
        select(User).filter_by(is_admin=True)
    )
    return result.scalars().all()


async def get_non_admin_users(db: AsyncSession = Depends(get_db)) -> Sequence[User]:
    result = await db.execute(
        select(User).filter_by(is_admin=False)
    )
    return result.scalars().all()


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
