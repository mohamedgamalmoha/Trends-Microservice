from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from shared_utils import messages
from shared_utils.exceptions import ObjDoesNotExist, ObjAlreadyExist

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserRetrieve
from app.services.user import UserService, get_user_service
from app.producer.api import UserMessageProducer, get_producer
from app.apiv2.deps import get_current_user, get_current_admin_user


user_router = APIRouter(
    prefix='/users',
    tags = ['users']
)


@user_router.get('/me/', status_code=status.HTTP_200_OK, response_model=UserRetrieve)
async def get_user_route(current_user: User = Depends(get_current_user)):
    return current_user


@user_router.post('/', status_code=status.HTTP_201_CREATED, response_model=UserRetrieve)
async def create_user_route(
        user_data: UserCreate,
        user_service: UserService=  Depends(get_user_service),
        producer: UserMessageProducer = Depends(get_producer)
    ):

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
    return await user_service.get_all()


@user_router.delete('/{user_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(
        user_id: int,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
    ):

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
