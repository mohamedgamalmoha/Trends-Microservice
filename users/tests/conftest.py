import dotenv
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from testcontainers.core.waiting_utils import wait_for_logs


async def lifespan(app):
    from shared_utils.db.session import init_db, close_db, drop_db

    await init_db()
    
    yield

    await drop_db()
    await close_db()


@pytest.fixture(scope="session")
def postgres_container():
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


@pytest.fixture(scope="function")
def app(postgres_container):
    from shared_utils.core.conf import settings
    
    dotenv.load_dotenv('.env.test')

    settings.SQLALCHEMY_DATABASE_URL = postgres_container.get_connection_url()

    from app.api.endpoints import auth, users, verification, password

    app = FastAPI(
        lifespan=lifespan,
        docs_url='/api/users/docs',
        redoc_url='/api/users/redoc',
        openapi_url='/api/users/openapi.json'
    )

    app.include_router(auth.auth_router, prefix='/api')
    app.include_router(users.user_router, prefix='/api')
    app.include_router(verification.email_verification_router, prefix='/api')
    app.include_router(password.password_reset_router, prefix='/api')

    return app


@pytest.fixture(scope="function")
def client(app):
    with TestClient(app) as test_client:
        yield test_client
