from datetime import datetime

from fastapi import Depends, HTTPException, status, APIRouter
from shared_utils import messages
from shared_utils.exceptions import ObjDoesNotExist

from app.utils import db_model_to_dict
from app.exceptions import TokenExpiredError, InvalidTokenError
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
    """
    Send an email verification token to a user who has not yet activated their account.

    This endpoint verifies that the user exists and is not already active. If valid,
    it generates a verification token and triggers a background message to send a
    verification email.

    Args:
        - user_data (UserEmailVerification): The user's email to verify.
        - user_service (UserService): Service used to retrieve user data from the database.
        - email_verification_service (EmailVerificationTokenService): Service to generate the verification token.
        - producer (UserMessageProducer): Message producer used to send the verification email event.

    Returns:
        - None: Returns HTTP 204 No Content upon successful processing.

    Raises:
        - HTTPException: 404 Not Found if the user with the given email does not exist.
        - HTTPException: 400 Bad Request if the user is already active.
    """
    try:
        db_user = await user_service.get_by_email(email=user_data.email)
    except ObjDoesNotExist:
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
    """
    Confirm a user's email address using a verification token and activate their account.

    This endpoint decodes the email verification token, validates it, checks for expiration,
    and activates the user account if everything is valid. Intended to be called when a user
    clicks the verification link sent to their email.

    Args:
        - user_data (UserEmailVerificationConfirmation): Contains the verification token.
        - user_service (UserService): Service to retrieve and update user data.
        - email_verification_service (EmailVerificationTokenService): Service to decode and verify the token.
        - producer (UserMessageProducer): Message producer for sending a confirmation event (TODO).

    Returns:
        - None: Returns HTTP 204 No Content upon successful email verification.

    Raises:
        - HTTPException: 400 Bad Request if the token is invalid or malformed.
        - HTTPException: 404 Not Found if the user does not exist or the token has expired.
    """
    try:
        payload =  email_verification_service.decode(token=user_data.verification_token)
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

    await user_service.update(id=db_user.id, is_active=True)

    # TODO: Send email confirmation using user producer
