import logging
from typing import Any

from app.conf import (USER_CREATION_RABBITMQ_QUEUE, USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE,
                      USER_PASSWORD_FORGET_RABBITMQ_QUEUE)


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


async def user_creation_handler(notification_data: Any) -> None:
    logger.info(f'Message received: {notification_data}')


async def user_email_verification_handler(notification_data: Any) -> None:
    logger.info(f'Message received: {notification_data}')


async def user_password_forget_handler(notification_data: Any) -> None:
    logger.info(f'Message received: {notification_data}')


USER_HANDLERS = {
    USER_CREATION_RABBITMQ_QUEUE.name: user_creation_handler,
    USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE.name: user_email_verification_handler,
    USER_PASSWORD_FORGET_RABBITMQ_QUEUE.name: user_password_forget_handler
}
