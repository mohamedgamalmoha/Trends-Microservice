from typing import Type, Sequence

from fastapi import Depends
from sqlalchemy.sql import select, exists, or_
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from src.users.models import User


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
