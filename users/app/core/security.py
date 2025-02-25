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


def create_token(email: str, expires_minutes: int, key: str, algorithm: str) -> str:

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    jwt_payload = {
        'email': email,
        'expire': expire.isoformat()
    }

    encoded_jwt = jwt.encode(
        payload=jwt_payload,
        key=key,
        algorithm=algorithm
    )

    return encoded_jwt


def decode_token(token: str, key: str, algorithm: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            jwt=token,
            key=key,
            algorithms=[algorithm],
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
