from contextlib import asynccontextmanager

from fastapi import FastAPI
from shared_utils.db.session import init_db, close_db

from app.producer.api import init_producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_producer()

    yield

    await close_db()
