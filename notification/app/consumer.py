import json
import logging
from typing import Optional, List

import aio_pika

from app.handlers import USER_HANDLERS
from app.conf import (
    settings, RabbitMQExchangeSettings, RabbitMQQueueSettings, USER_RABBITMQ_EXCHANGE, USER_RABBITMQ_QUEUES,
    USER_CREATION_RABBITMQ_QUEUE, USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE, USER_PASSWORD_FORGET_RABBITMQ_QUEUE
)


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class MessageConsumer:
    """
    A simplified consumer for handling user-related messages from RabbitMQ.
    """
    connection: Optional[aio_pika.abc.AbstractConnection] = None
    channel: Optional[aio_pika.abc.AbstractChannel] = None
    exchange: Optional[aio_pika.abc.AbstractExchange] = None

    def __init__(self, url: str, exchange_settings: RabbitMQExchangeSettings,
                  queues_settings: List[RabbitMQQueueSettings]) -> None:
        self.url = url
        self.exchange_settings = exchange_settings
        self.queues_settings = queues_settings

    async def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)

    def is_connected(self) -> bool:
        """
        Check if the connection to RabbitMQ is active.
        """
        return bool(
            self.connection
            and not self.connection.is_closed
            and self.channel
            and not self.channel.is_closed
        )

    async def declare_exchange(self) -> None:
        """
        Declare the RabbitMQ exchange.
        """
        if not self.is_connected():
            await self.connect()

        self.exchange = await self.channel.declare_exchange(
            name=self.exchange_settings.name,
            type=self.exchange_settings.type,
            durable=self.exchange_settings.durable,
            robust=self.exchange_settings.robust
        )

    async def declare_queues(self) -> None:
        """
        Declare all configured RabbitMQ queues.
        """
        if not self.is_connected():
            await self.connect()

        if not self.exchange:
            await self.declare_exchange()

        for queue_settings in self.queues_settings:
            queue = await self.channel.declare_queue(
                name=queue_settings.name,
                durable=queue_settings.durable,
                robust=queue_settings.robust
            )
            await queue.bind(self.exchange_settings.name, routing_key=queue_settings.name)
            await queue.consume(self.process_message)
            logger.info(f"Set up queue: {queue_settings.name}")

    async def process_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        """
        Process incoming messages based on their routing key.
        """
        async with message.process():
            try:
                routing_key = message.routing_key
                body = json.loads(message.body.decode())
                await self.message_handler(routing_key=routing_key, message=body)
            except json.JSONDecodeError:
                logger.error("Failed to decode message body")
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def message_handler(self, routing_key, message):
        logger.info(f"Received message with routing key {routing_key}: {message}")

    async def start(self) -> None:
        """Start the consumer."""
        await self.connect()
        await self.declare_exchange()
        await self.declare_queues()
        logger.info("Consumer started successfully")

    async def close(self) -> None:
        """Close the connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Consumer connection closed")


class UserConsumer(MessageConsumer):

    async def message_handler(self, routing_key, message):
        try:
            handler_function = USER_HANDLERS[routing_key]
            await handler_function(message)
        except Exception as e:
            logger.error(f"Error handling message: {e}")
