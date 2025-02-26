from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, APIRouter

from app import messages
from app.db.session import get_db
from app.repositories.user import get_user_by_email, reset_user_password
from app.schemas.password import UserPasswordReset, UsePasswordResetConfirmation
from app.schemas.producer import UserResetPasswordProducerMessage, UserResetPasswordConfirmationProducerMessage
from app.utils import db_model_to_dict
from app.producer.api import send_user_email_verification_message
from app.api.deps import create_password_reset_token, decode_password_reset_token


password_reset_router = APIRouter(
    prefix="/password-reset",
    tags=["password reset"]
)


@password_reset_router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(user_data: UserPasswordReset, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(email=user_data.email, db=db)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND_MESSAGE
    )

    user_data = db_model_to_dict(instance=db_user)

    reset_token = create_password_reset_token(email=user_data.email)

    user = UserResetPasswordProducerMessage(
        **user_data,
        reset_token=reset_token
    )

    await send_user_email_verification_message(user_data=user)


@password_reset_router.post("/confirm/", status_code=status.HTTP_200_OK)
async def confirm_password_reset(user_data: UsePasswordResetConfirmation, db: AsyncSession = Depends(get_db)):

    pyload =  decode_password_reset_token(token=user_data.reset_token)
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

    await reset_user_password(user_id=db_user.id, new_password=user_data.new_password, db=db)

    # TODO: Send password reset  confirm using user producer
