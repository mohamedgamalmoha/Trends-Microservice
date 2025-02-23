from typing import Dict, Any
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from app.core.conf import settings
from app.exceptions import InvalidTokenError, TokenExpiredError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


pwd_context = CryptContext(schemes=[settings.PASSWORD_CRYPT_CONTEXT_SCHEMA], deprecated='auto')


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(email: str, expires_delta: timedelta | None = None) -> str:

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    jwt_payload = {
        'email': email,
        'expire': expire.isoformat()
    }

    encoded_jwt = jwt.encode(
        payload=jwt_payload,
        key=settings.SECRET_KEY,
        algorithm=settings.ACCESS_TOKEN_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ACCESS_TOKEN_ALGORITHM],
            options={"verify_exp": False}
        )
        email = payload.get("email")
        if email is None:
            raise InvalidTokenError()
    except jwt.exceptions.ExpiredSignatureError:
        raise TokenExpiredError()
    except (jwt.exceptions.DecodeError, jwt.PyJWTError):
        raise InvalidTokenError()
    else:
        return payload
