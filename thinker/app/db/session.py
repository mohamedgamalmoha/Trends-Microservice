from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.db.base import Base
from app.core.conf import settings
from app.utils import safe_call


engine = create_async_engine(
    url=settings.SQLALCHEMY_DATABASE_URL
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autocommit=False)


@safe_call
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@safe_call
async def close_db() -> None:
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session
