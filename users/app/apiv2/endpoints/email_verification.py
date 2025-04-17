from datetime import datetime

from fastapi import Depends, HTTPException, status, APIRouter
from shared_utils import messages

from app.utils import db_model_to_dict
from app.schemas.verification import UserEmailVerification, UserEmailVerificationConfirmation
from app.schemas.producer import UserEmailVerificationProducerMessage
from app.services.user import UserService, get_user_service
from app.services.email_verification_token import EmailVerificationTokenService, get_email_verification_token_service
from app.producer.api import UserMessageProducer, get_producer


email_verification_router = APIRouter(
    prefix="/email-verification",
    tags=["email-verification"]
)


@email_verification_router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def send_email_verification(
        user_data: UserEmailVerification,
        user_service: UserService = Depends(get_user_service),
        email_verification_service: EmailVerificationTokenService = Depends(get_email_verification_token_service),
        producer: UserMessageProducer = Depends(get_producer)
    ):

    db_user = await user_service.get_by_email(email=user_data.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND_MESSAGE
        )

    if db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.USER_ALREADY_ACTIVE
        )

    user_data_dict = db_model_to_dict(instance=db_user)

    verification_token = email_verification_service.create(email=user_data.email)

    user = UserEmailVerificationProducerMessage(
        **user_data_dict,
        verification_token=verification_token
    )

    await producer.send_user_email_verification_message(
        user_data=user.model_dump()
    )


@email_verification_router.post("/confirm/", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_email_verification(
        user_data: UserEmailVerificationConfirmation,
        user_service: UserService = Depends(get_user_service),
        email_verification_service: EmailVerificationTokenService = Depends(get_email_verification_token_service),
        producer: UserMessageProducer = Depends(get_producer)
    ):

    pyload =  email_verification_service.decode(token=user_data.verification_token)

    email = pyload.get('email', None)

    db_user = await user_service.get_by_email(email=email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND_MESSAGE
    )

    expire = pyload.get('expire', None)
    if expire and datetime.fromisoformat(expire) < datetime.now():
      raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.EXPIRED_TOKEN_MESSAGE
    )

    await user_service.update(id=db_user.id, is_active=True)

    # TODO: Send email confirmation using user producer
