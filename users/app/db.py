from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.conf import settings


engine = create_async_engine(
    url=settings.SQLALCHEMY_DATABASE_URL
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autocommit=False)

Base = declarative_base()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
