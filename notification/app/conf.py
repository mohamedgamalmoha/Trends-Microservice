import os
import logging
from typing import Optional

import dotenv
import aio_pika
from pydantic_settings import BaseSettings


dotenv.load_dotenv('../.env')

logging.basicConfig(level=logging.INFO)


class Settings(BaseSettings):
    RABBITMQ_URL: str = os.environ.get('RABBITMQ_URL')


class RabbitMQQueueSettings(BaseSettings):
    name: str
    durable: Optional[bool] = True
    robust: Optional[bool] = True


class RabbitMQExchangeSettings(BaseSettings):
    name: str
    type: Optional[aio_pika.ExchangeType] = aio_pika.ExchangeType.DIRECT
    durable: Optional[bool] = True
    robust: Optional[bool] = True


settings = Settings()


USER_CREATION_RABBITMQ_QUEUE = RabbitMQQueueSettings(
    name=os.environ.get('USER_CREATION_RABBITMQ_QUEUE_NAME')
)

USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE = RabbitMQQueueSettings(
    name=os.environ.get('USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE_NAME')
)

USER_PASSWORD_FORGET_RABBITMQ_QUEUE = RabbitMQQueueSettings(
    name=os.environ.get('USER_PASSWORD_FORGET_RABBITMQ_QUEUE_NAME')
)

USER_RABBITMQ_QUEUES = [
    USER_CREATION_RABBITMQ_QUEUE,
    USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE,
    USER_PASSWORD_FORGET_RABBITMQ_QUEUE
]

USER_RABBITMQ_EXCHANGE = RabbitMQExchangeSettings(
    name=os.environ.get('USER_RABBITMQ_EXCHANGE_NAME', 'user_exchange')
)
