import json
from typing import List, Optional, Any

import aio_pika

from app.producer.json import CustomJSONEncoder
from app.producer.conf import (RabbitMQExchangeSettings, RabbitMQQueueSettings, USER_CREATION_RABBITMQ_QUEUE,
                  USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE, USER_PASSWORD_FORGET_RABBITMQ_QUEUE)


class MessageProducer:
    """
    A class to handle RabbitMQ message production.
    """
    connection: Optional[aio_pika.abc.AbstractConnection] = None
    channel: Optional[aio_pika.abc.AbstractChannel] = None
    exchange: Optional[aio_pika.abc.AbstractExchange] = None

    def __init__( self, url: str, exchange_settings: RabbitMQExchangeSettings,
                  queues_settings: List[RabbitMQQueueSettings]) -> None:
        self.url = url
        self.exchange_settings = exchange_settings
        self.queues_settings = queues_settings

    async def connect(self) -> None:
        """
        Establish connection to RabbitMQ server.
        """
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()

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

        for queue_setting in self.queues_settings:
            queue= await self.channel.declare_queue(
                name=queue_setting.name,
                durable=queue_setting.durable,
                robust=queue_setting.robust
            )
            await queue.bind(self.exchange)

    @staticmethod
    def prepare_message(message_data: Any) -> aio_pika.Message:
        """
        Prepare a message for publishing.

        Args:
            - message_data: The data to be sent in the message

        Returns:
            - aio_pika.Message: The prepared message
        """
        return aio_pika.Message(
            body=json.dumps(message_data, cls=CustomJSONEncoder).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )

    async def send_message(self, routing_key: str, message_data: Any) -> None:
        """
        Send a message to the specified routing key.

        Args:
            - routing_key: The routing key for message delivery
            - message_data: The data to be sent
        """
        if not self.exchange:
            await self.declare_exchange()

        message = self.prepare_message(message_data)
        await self.exchange.publish(message, routing_key=routing_key)

    async def close(self) -> None:
        """
        Close the RabbitMQ connection.
        """
        if self.connection and not self.connection.is_closed:
            await self.connection.close()


class UserMessageProducer(MessageProducer):

    async def init_user_producer(self)  -> None:
        await self.connect()
        await self.declare_exchange()
        await self.declare_queues()

    async def send_user_creation_message(self, message_data: Any) -> None:
        await self.send_message(
            routing_key=USER_CREATION_RABBITMQ_QUEUE.name,
            message_data=message_data
        )

    async def send_user_email_verification_message(self, message_data: Any) -> None:
        await self.send_message(
            routing_key=USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE.name,
            message_data=message_data
        )

    async def send_user_password_forget_message(self, message_data: Any) -> None:
        await self.send_message(
            routing_key=USER_PASSWORD_FORGET_RABBITMQ_QUEUE.name,
            message_data=message_data
        )
