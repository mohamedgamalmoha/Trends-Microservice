from typing import Dict, Any
from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import constants
from conf import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


pwd_context = CryptContext(schemes=[settings.PASSWORD_CRYPT_CONTEXT_SCHEMA], deprecated='auto')


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(payload: dict, expires_delta: timedelta | None = None) -> str:
    assert 'sub' in payload

    jwt_payload = payload.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    jwt_payload.update({"exp": expire})

    encoded_jwt = jwt.encode(
        payload=jwt_payload,
        key=settings.SECRET_KEY,
        algorithm=[settings.ACCESS_TOKEN_ALGORITHM]
    )

    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            message=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ACCESS_TOKEN_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=constants.INVALID_TOKEN_MESSAGE
            )
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=constants.EXPIRED_TOKEN_MESSAGE
        )
    except (jwt.exceptions.DecodeError, jwt.PyJWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=constants.INVALID_TOKEN_MESSAGE
        )
    else:
        return payload
