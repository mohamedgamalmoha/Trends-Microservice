from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.producer.api import init_producer
from app.db.session import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_producer()

    yield

    await close_db()
