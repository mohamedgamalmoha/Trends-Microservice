from fastapi import APIRouter, Depends, HTTPException, status
from shared_utils import messages

from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserLogin
from app.services.auth import AuthService, get_auth_service
from app.services.access_token import AccessTokenService, get_access_token_service
from app.api.deps import get_current_user


auth_router = APIRouter(
    prefix='/jwt',
    tags = ['auth']
)


@auth_router.post('/create/', status_code=status.HTTP_200_OK, response_model=Token)
async def create_jwt_route(
        user_data: UserLogin,
        auth_service: AuthService = Depends(get_auth_service),
        access_token_service: AccessTokenService = Depends(get_access_token_service)
    ):
    """
    Authenticate a user using email and password, and issue a JWT access token.

    This endpoint verifies the user's credentials and, upon successful authentication,
    returns a new JWT access token.

    Args:
        - user_data (UserLogin): The user's login credentials (email and password).
        - auth_service (AuthService): Service used to authenticate the user.
        - access_token_service (AccessToken): Service used to generate JWT tokens.

    Returns:
        - Token: A response containing the newly created JWT access token.

    Raises:
        - HTTPException: 401 Unauthorized if the credentials are invalid.
    """
    user = await auth_service.authenticate_basic(email=user_data.email, password=user_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_CREDENTIALS_MESSAGE
        )

    access_token = access_token_service.create(email=user.email)

    return Token(access_token=access_token)


@auth_router.get('/verify/', status_code=status.HTTP_204_NO_CONTENT)
async def verify_jwt_token_route(current_user: User = Depends(get_current_user)):
    """
    Verify the validity of a provided JWT access token.

    This endpoint checks if the current token is valid by retrieving the user
    from it. If the token is valid and the user exists, a 204 No Content
    response is returned.

    Args:
        - current_user (User): The authenticated user derived from the token.

    Raises:
        - HTTPException: 401 Unauthorized if the token is invalid or user is not found.

    Returns:
        - None: Returns HTTP 204 No Content on successful verification.
    """
    ...
