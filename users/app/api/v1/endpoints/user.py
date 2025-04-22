from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from shared_utils import messages
from shared_utils.exceptions import ObjDoesNotExist, ObjAlreadyExist

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserRetrieve
from app.services.user import UserService, get_user_service
from app.producer.api import UserMessageProducer, get_producer
from app.api.deps import get_current_user, get_current_admin_user


user_router = APIRouter(
    prefix='/users',
    tags = ['users']
)


@user_router.get('/me/', status_code=status.HTTP_200_OK, response_model=UserRetrieve)
async def get_user_route(current_user: User = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user's profile.

    This endpoint returns information about the user associated with the
    provided JWT access token.

    Args:
        - current_user (User): The authenticated user, resolved from the access token.

    Returns:
        - UserRetrieve: The current user's profile information.

    Raises:
        - HTTPException: 401 Unauthorized if the token is invalid or the user cannot be authenticated.
    """
    return current_user


@user_router.post('/', status_code=status.HTTP_201_CREATED, response_model=UserRetrieve)
async def create_user_route(
        user_data: UserCreate,
        user_service: UserService=  Depends(get_user_service),
        producer: UserMessageProducer = Depends(get_producer)
    ):
    """
    Create a new user account and send verification and onboarding messages.

    This endpoint registers a new user, excluding password confirmation, and
    sends both a user creation event and an email verification message via a message producer.

    Args:
        - user_data (UserCreate): The data required to create a new user, including email and password.
        - user_service (UserService): Service responsible for creating and persisting the user.
        - producer (UserMessageProducer): Service used to send asynchronous user-related messages.

    Returns:
        - UserRetrieve: The newly created user's profile information.

    Raises:
        - HTTPException: 409 Conflict if a user with the same email already exists.
    """
    data = user_data.model_dump(exclude=['password_confirm'])

    try:
        db_user = await user_service.create(
            **data
        )
    except ObjAlreadyExist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.USER_ALREADY_EXIST_MESSAGE
        )

    ret_user = UserRetrieve.from_orm(db_user)

    await producer.send_user_creation_message(
        message_data=ret_user.model_dump()
    )

    await producer.send_user_email_verification_message(
        message_data=ret_user.model_dump()
    )

    return ret_user


@user_router.get('/{user_id}/', status_code=status.HTTP_200_OK, response_model=UserRetrieve)
async def get_user_route(
        user_id: int,
        current_user: User = Depends(get_current_user),
        user_service: UserService=  Depends(get_user_service),
    ):
    """
    Retrieve a user's profile by their user ID.

    This endpoint fetches the profile of a user by their ID. The requesting user must either
    be an admin or the same user as the one whose profile is being requested.

    Args:
        - user_id (int): The ID of the user whose profile is being requested.
        - current_user (User): The authenticated user requesting the profile, extracted from the token.
        - user_service (UserService): Service used to retrieve user data from the database.

    Returns:
        - UserRetrieve: The requested user's profile information.

    Raises:
        - HTTPException: 404 Not Found if the user with the specified ID does not exist.
        - HTTPException: 403 Forbidden if the requesting user is neither an admin nor the same user.
    """
    try:
        user = await user_service.get_by_id(id=user_id)
    except ObjDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND_MESSAGE
        )

    if not (current_user.is_admin or current_user.id == user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    return user


@user_router.get('/', status_code=status.HTTP_200_OK, response_model=List[UserRetrieve])
async def get_users_route(
        current_user: User = Depends(get_current_admin_user),
        user_service: UserService = Depends(get_user_service)
    ):
    """
    Retrieve a list of all users.

    This endpoint retrieves a list of all users. It requires the requesting user to be an admin.

    Args:
        - current_user (User): The authenticated user, validated as an admin, who is requesting the list.
        - user_service (UserService): Service used to retrieve all users from the database.

    Returns:
        - List[UserRetrieve]: A list of all user profiles.

    Raises:
        - HTTPException: 403 Forbidden if the requesting user is not an admin.
    """
    return await user_service.get_all()


@user_router.delete('/{user_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(
        user_id: int,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
    ):
    """
    Delete a user account by their user ID.

    This endpoint allows an admin or the user themselves to delete a user account.
    The requesting user must either be an admin or the user whose account is being deleted.

    Args:
        - user_id (int): The ID of the user to be deleted.
        - current_user (User): The authenticated user attempting to delete the user account.
        - user_service (UserService): Service used to retrieve and delete the user.

    Returns:
        - None: Returns HTTP 204 No Content upon successful deletion of the user.

    Raises:
        - HTTPException: 404 Not Found if the user with the specified ID does not exist.
        - HTTPException: 403 Forbidden if the requesting user is not an admin or the user themselves.
    """
    try:
        user = await user_service.get_by_id(id=user_id)
    except ObjDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND_MESSAGE
        )

    if not (current_user.is_admin or current_user.id == user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    await user_service.delete(id=user.id)


@user_router.put('/{user_id}/', status_code=status.HTTP_200_OK, response_model=UserRetrieve)
async def update_user_route(
        user_id: int,
        user_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
    ):
    """
    Update a user's profile information.

    This endpoint allows an admin or the user themselves to update their user profile information.
    The requesting user must either be an admin or the user whose profile is being updated.

    Args:
        - user_id (int): The ID of the user whose profile is being updated.
        - user_data (UserUpdate): The data to update the user's profile with (excluding any fields
          such as password that may require additional logic).
        - current_user (User): The authenticated user attempting to update the profile.
        - user_service (UserService): Service used to retrieve and update the user's data in the database.

    Returns:
        - UserRetrieve: The updated user profile information.

    Raises:
        - HTTPException: 404 Not Found if the user with the specified ID does not exist.
        - HTTPException: 403 Forbidden if the requesting user is not an admin or the user themselves.
    """
    try:
        user = await user_service.get_by_id(id=user_id)
    except ObjDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND_MESSAGE
        )

    if not (current_user.is_admin or current_user.id == user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    data = user_data.model_dump()
    return await user_service.update(id=user.id, **data)
