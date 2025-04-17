from datetime import datetime

from fastapi import Depends, HTTPException, status, APIRouter
from shared_utils import messages

from app.utils import db_model_to_dict
from app.schemas.password import UserPasswordReset, UsePasswordResetConfirmation
from app.schemas.producer import UserResetPasswordProducerMessage, UserResetPasswordConfirmationProducerMessage
from app.services.user import UserService, get_user_service
from app.services.password_reset_token import PasswordResetTokenService, get_password_reset_token_service
from app.producer.api import UserMessageProducer, get_producer


password_reset_router = APIRouter(
    prefix="/password-reset",
    tags=["password reset"]
)


@password_reset_router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(
        user_data: UserPasswordReset,
        user_service: UserService = Depends(get_user_service),
        password_reset_service: PasswordResetTokenService = Depends(get_password_reset_token_service),
        producer: UserMessageProducer = Depends(get_producer)
    ):

    db_user = await user_service.get_by_email(email=user_data.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND_MESSAGE
    )

    user_data = db_model_to_dict(instance=db_user)

    reset_token = password_reset_service.create(email=user_data.email)

    user = UserResetPasswordProducerMessage(
        **user_data,
        reset_token=reset_token
    )

    await producer.send_user_email_verification_message(
        user_data=user.model_dump()
    )


@password_reset_router.post("/confirm/", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
        user_data: UsePasswordResetConfirmation,
        user_service: UserService = Depends(get_user_service),
        password_reset_service: PasswordResetTokenService = Depends(get_password_reset_token_service),
        producer: UserMessageProducer = Depends(get_producer)
    ):

    payload =  password_reset_service.decode(token=user_data.reset_token)

    db_user = await user_service.get_by_email(email=payload['email'])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND_MESSAGE
        )

    expire = payload.get('expire', None)
    if expire and datetime.fromisoformat(expire) < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.EXPIRED_TOKEN_MESSAGE
        )

    await user_service.set_password(id=db_user.id, new_password=user_data.new_password)

    # TODO: Send password reset  confirm using user producer
