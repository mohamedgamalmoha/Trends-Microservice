from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    yield

    await close_db()
