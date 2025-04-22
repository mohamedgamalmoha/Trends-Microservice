import json
import dotenv
import pytest
import pytest_asyncio
import aio_pika
from fastapi import FastAPI
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from testcontainers.core.waiting_utils import wait_for_logs

from tests.utils.lifespan import lifespan
from tests.utils.producer import get_custom_producer
from tests.utils.rabbitmq import CustomRabbitMqContainer


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
def app_setup_and_teardown(postgres_container):
    dotenv.load_dotenv('.env.test')

    import os
    os.environ['SQLALCHEMY_DATABASE_URL'] = postgres_container.get_connection_url()

    yield


@pytest.fixture(scope="function")
def app(app_setup_and_teardown):
    from app.api.v1 import v1_api_router
    from app.producer.api import get_producer

    app = FastAPI(
        lifespan=lifespan
    )

    app.include_router(v1_api_router, prefix='/api')

    app.dependency_overrides[get_producer] = get_custom_producer

    return app


@pytest.fixture(scope="function")
def client(app):
    with TestClient(app) as test_client:
        yield test_client


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


@pytest.fixture(scope="session")
def producer_setup_and_teardown(rabbitmq_container):
    dotenv.load_dotenv('.env.test')

    import os
    os.environ['RABBITMQ_URL'] = rabbitmq_container.get_connection_url()

    yield


@pytest_asyncio.fixture
async def producer(producer_setup_and_teardown):
    from app.producer.conf import settings, USER_RABBITMQ_EXCHANGE, USER_RABBITMQ_QUEUES
    from app.producer.producer import UserMessageProducer

    user_producer = UserMessageProducer(
        url=settings.RABBITMQ_URL,
        exchange_settings=USER_RABBITMQ_EXCHANGE,
        queues_settings=USER_RABBITMQ_QUEUES
    )

    await user_producer.connect()
    
    await user_producer.declare_exchange()
    await user_producer.declare_queues()

    yield user_producer
    
    await user_producer.close()


@pytest_asyncio.fixture
async def consumer_received_messages(producer_setup_and_teardown):
    from app.producer.conf import settings, USER_CREATION_RABBITMQ_QUEUE, USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE, USER_PASSWORD_FORGET_RABBITMQ_QUEUE
    
    connection = await aio_pika.connect_robust(
        settings.RABBITMQ_URL
    )
    channel = await connection.channel()
    
    # Dictionary to store received messages by queue
    received_messages = {
        USER_CREATION_RABBITMQ_QUEUE.name: [],
        USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE.name: [],
        USER_PASSWORD_FORGET_RABBITMQ_QUEUE.name: []
    }
    
    # Create message handlers for each queue
    async def create_consumer(queue_name):
        async def message_handler(message):
            async with message.process():
                received_messages[queue_name].append(json.loads(message.body.decode()))
        
        queue = await channel.get_queue(queue_name)
        await queue.consume(message_handler)
        
    # Set up consumers for each queue
    for queue_name in received_messages.keys():
        await create_consumer(queue_name)
    
    yield received_messages
    
    # Cleanup
    await connection.close()
