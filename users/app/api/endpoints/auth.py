from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from app import messages
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserRetrieve
from app.api.deps import authenticate_user, get_current_user, create_access_token


auth_router = APIRouter(
    prefix='/jwt',
    tags = ['auth']
)


@auth_router.post('/create/', status_code=status.HTTP_200_OK, response_model=Token)
async def create_jwt_route(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(email=user_data.email, password=user_data.password, db=db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_CREDENTIALS_MESSAGE
        )

    access_token = create_access_token(email=user.email)

    return Token(access_token=access_token)


@auth_router.get('/verify/', status_code=status.HTTP_204_NO_CONTENT)
async def verify_jwt_token_route(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ...
