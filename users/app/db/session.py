from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.conf import settings


engine = create_async_engine(
    url=settings.SQLALCHEMY_DATABASE_URL
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autocommit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
