import dotenv
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from testcontainers.rabbitmq import RabbitMqContainer
from testcontainers.core.waiting_utils import wait_for_logs


class CustomRabbitMqContainer(RabbitMqContainer):

    def get_connection_url(self):
        return f"amqp://{self.username}:{self.password}@{self.get_container_host_ip()}:{self.get_exposed_port(self.port)}"


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


@pytest.fixture(scope="session")
def rabbitmq_container():
    rabbitmq = CustomRabbitMqContainer(
        image="rabbitmq:4.0.6-alpine",
    ).with_exposed_ports(
        5672
    )
    
    rabbitmq.start()
    
    wait_for_logs(
        rabbitmq,
        "Server startup complete"
    )
    
    yield rabbitmq
    
    rabbitmq.stop()


@pytest.fixture(scope="function")
def setup_and_teardown(postgres_container, rabbitmq_container):
    dotenv.load_dotenv('.env.test')

    import os
    os.environ['SQLALCHEMY_DATABASE_URL'] = postgres_container.get_connection_url()
    os.environ['RABBITMQ_URL'] = rabbitmq_container.get_connection_url()

    yield


@pytest.fixture(scope="function")
def app(setup_and_teardown):
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
