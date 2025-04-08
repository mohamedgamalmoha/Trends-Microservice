from shared_utils.utils import safe_call

from app.producer.conf import settings, USER_RABBITMQ_EXCHANGE, USER_RABBITMQ_QUEUES
from app.schemas.producer import (UserCreationProducerMessage, UserEmailVerificationProducerMessage,
                                  UserResetPasswordProducerMessage)
from app.producer.producer import UserMessageProducer


def get_producer() -> UserMessageProducer:
    return UserMessageProducer(
        url=settings.RABBITMQ_URL,
        exchange_settings=USER_RABBITMQ_EXCHANGE,
        queues_settings=USER_RABBITMQ_QUEUES
    )


@safe_call
async def init_producer() -> None:
    producer = get_producer()
    await producer.init_user_producer()
