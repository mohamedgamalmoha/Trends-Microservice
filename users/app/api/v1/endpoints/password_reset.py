from datetime import datetime

from fastapi import Depends, HTTPException, status, APIRouter
from shared_utils import messages
from shared_utils.exceptions import ObjDoesNotExist

from app.utils import db_model_to_dict
from app.exceptions import TokenExpiredError, InvalidTokenError
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
    """
    Initiate the password reset process by generating a reset token and sending a reset email.

    This endpoint receives the user's email, verifies the user exists, generates a password reset
    token, and sends an email with the reset instructions via a message producer.

    Args:
        - user_data (UserPasswordReset): The email address of the user requesting a password reset.
        - user_service (UserService): Service used to retrieve the user from the database.
        - password_reset_service (PasswordResetTokenService): Service to generate the reset token.
        - producer (UserMessageProducer): Message producer used to send the reset email event.

    Returns:
        - None: Returns HTTP 204 No Content upon successful request initiation.

    Raises:
        - HTTPException: 404 Not Found if the user with the given email does not exist.
    """
    try:
        db_user = await user_service.get_by_email(email=user_data.email)
    except ObjDoesNotExist:
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
    """
    Confirm and complete the password reset process using a valid reset token.

    This endpoint verifies the reset token, ensures it hasn't expired, and updates the user's
    password if everything is valid. It should also trigger a notification (e.g., email) that
    the password was successfully changed.

    Args:
        - user_data (UsePasswordResetConfirmation): Contains the reset token and new password.
        - user_service (UserService): Service for fetching and updating the user's data.
        - password_reset_service (PasswordResetTokenService): Service to validate the token.
        - producer (UserMessageProducer): Message producer for post-reset notifications (TODO).

    Returns:
        - None: Returns HTTP 200 OK upon successful password reset.

    Raises:
        - HTTPException: 400 Bad Request if the token is invalid or expired.
        - HTTPException: 404 Not Found if the user does not exist or the token is expired.
        - HTTPException: 400 Bad Request if token payload is malformed or missing required data.
    """
    try:
        payload =  password_reset_service.decode(token=user_data.reset_token)
        db_user = await user_service.get_by_email(email=payload['email'])
    except (TokenExpiredError, InvalidTokenError) as e:
       raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ObjDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND_MESSAGE
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.INVALID_TOKEN_MESSAGE,
        )

    expire = payload.get('expire', None)
    if expire and datetime.fromisoformat(expire) < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.EXPIRED_TOKEN_MESSAGE
        )

    await user_service.set_password(id=db_user.id, new_password=user_data.new_password)

    # TODO: Send password reset  confirm using user producer
