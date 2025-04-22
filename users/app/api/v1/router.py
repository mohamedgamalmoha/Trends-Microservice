from fastapi import APIRouter

from app.api.v1.endpoints import auth, user, email_verification, password_reset


v1_api_router = APIRouter(
    prefix='/v1'
)

v1_api_router.include_router(auth.auth_router)
v1_api_router.include_router(user.user_router)
v1_api_router.include_router(email_verification.email_verification_router)
v1_api_router.include_router(password_reset.password_reset_router)
