import dotenv
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from testcontainers.core.waiting_utils import wait_for_logs
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


dotenv.load_dotenv('.env.test')

Base = declarative_base()


@pytest.fixture(scope="module")
def postgres_container():
    # Start a PostgreSQL container with Testcontainers
    postgres = PostgresContainer(
        image="postgres:17.4-alpine",
        driver="asyncpg"
    ).with_exposed_ports(
        5432
    )
    
    postgres.start()
    
    wait_for_logs(
        postgres,
        "database system is ready to accept connections"
    )
    
    yield postgres
    
    postgres.stop()


@pytest_asyncio.fixture(scope='module')
async def engine(postgres_container):

    engine = create_async_engine(
        url=postgres_container.get_connection_url()
    )

    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.drop_all
        )

    await engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def session_local(engine):
    session_local = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False
    )
    return session_local


@pytest_asyncio.fixture(scope='function')
async def get_db(session_local):
    async with session_local() as session:
        yield session
        await session.rollback()  # Ensure clean state between tests


@pytest.fixture(scope="module")
def app(postgres_container, get_db):
    from shared_utils.core.conf import settings

    settings.SQLALCHEMY_DATABASE_URL = postgres_container.get_connection_url()

    from shared_utils.db.session import get_db as default_get_db
    from app.api.endpoints import auth, users, verification, password


    test_app = FastAPI(
        docs_url='/api/users/docs',
        redoc_url='/api/users/redoc',
        openapi_url='/api/users/openapi.json'
    )

    test_app.include_router(auth.auth_router, prefix='/api')
    test_app.include_router(users.user_router, prefix='/api')
    test_app.include_router(verification.email_verification_router, prefix='/api')
    test_app.include_router(password.password_reset_router, prefix='/api')

    test_app.dependency_overrides[default_get_db] = get_db

    return test_app


@pytest.fixture(scope="module")
def client(app):
    with TestClient(app) as client:
        yield client
