from fastapi import APIRouter, Depends, HTTPException, status
from shared_utils import messages

from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserLogin
from app.services.user import UserService, get_user_service
from app.services.auth import AuthService, get_auth_service
from app.apiv2.deps import get_current_user


auth_router = APIRouter(
    prefix='/jwt',
    tags = ['auth']
)


@auth_router.post('/create/', status_code=status.HTTP_200_OK, response_model=Token)
async def create_jwt_route(
        user_data: UserLogin,
        auth_service: AuthService = Depends(get_auth_service)
    ):
    user = await auth_service.authenticate(email=user_data.email, password=user_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_CREDENTIALS_MESSAGE
        )

    access_token = await auth_service.create_auth_token(email=user.email)

    return Token(access_token=access_token)


@auth_router.get('/verify/', status_code=status.HTTP_204_NO_CONTENT)
async def verify_jwt_token_route(current_user: User = Depends(get_current_user)):
    ...
