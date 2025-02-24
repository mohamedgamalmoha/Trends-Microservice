from app.conf import settings, USER_RABBITMQ_EXCHANGE, USER_RABBITMQ_QUEUES
from app.consumer import UserConsumer


def get_consumer() -> UserConsumer:
    return UserConsumer(
        url=settings.RABBITMQ_URL,
        exchange_settings=USER_RABBITMQ_EXCHANGE,
        queues_settings=USER_RABBITMQ_QUEUES
    )
