from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, APIRouter
from shared_utils import messages
from shared_utils.db.session import get_db

from app.core.security import create_email_verification_token, decode_email_verification_token
from app.repositories.user import get_user_by_email, activate_user
from app.schemas.verification import UserEmailVerification, UserEmailVerificationConfirmation
from app.schemas.producer import UserEmailVerificationProducerMessage
from app.utils import db_model_to_dict
from app.producer.api import get_producer
from app.producer.producer import UserMessageProducer


email_verification_router = APIRouter(
    prefix="/email-verification",
    tags=["email-verification"]
)


@email_verification_router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def send_email_verification(
        user_data: UserEmailVerification,
        db: AsyncSession = Depends(get_db),
        producer: UserMessageProducer = Depends(get_producer)
    ):

    db_user = await get_user_by_email(email=user_data.email, db=db)
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

    verification_token = create_email_verification_token(email=user_data.email)

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
        db: AsyncSession = Depends(get_db)
    ):

    pyload =  decode_email_verification_token(token=user_data.verification_token)
    email = pyload.get('email', None)

    db_user = await get_user_by_email(email=email, db=db)
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

    await activate_user(user_id=db_user.id, db=db)

    # TODO: Send email confirmation using user producer
