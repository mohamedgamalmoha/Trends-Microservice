from app.schemas.user import UserRetrieve
from app.producer.producer import UserMessageProducer
from app.producer.conf import settings, USER_RABBITMQ_EXCHANGE, USER_RABBITMQ_QUEUES


def get_producer() -> UserMessageProducer:
    return UserMessageProducer(
        url=settings.RABBITMQ_URL,
        exchange_settings=USER_RABBITMQ_EXCHANGE,
        queues_settings=USER_RABBITMQ_QUEUES
    )


async def init_producer() -> None:
    producer = get_producer()
    await producer.init_user_producer()


async def send_user_creation_message(user_data: UserRetrieve) -> None:
    producer =  get_producer()
    await producer.send_user_creation_message(
        message_data=user_data.model_dump()
    )


async def send_user_email_verification_message(user_data: UserRetrieve) -> None:
    producer = get_producer()
    await producer.send_user_email_verification_message(
        message_data=user_data.model_dump()
    )


async def send_user_password_forget_message(user_data: UserRetrieve) -> None:
    producer = get_producer()
    await producer.send_user_password_forget_message(
        message_data=user_data.model_dump()
    )
