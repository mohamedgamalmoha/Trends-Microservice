from typing import Any


class CustomUserMessageProducer:

    async def init_user_producer(self)  -> None:
        ...

    async def send_user_creation_message(self, message_data: Any) -> None:
        ...

    async def send_user_email_verification_message(self, message_data: Any) -> None:
        ...

    async def send_user_password_forget_message(self, message_data: Any) -> None:
        ...


def get_custom_producer():
    return CustomUserMessageProducer()
