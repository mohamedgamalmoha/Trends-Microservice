from typing import Dict, Any, Type
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import messages
from conf import settings
from db import get_db
from models import User
from query import get_user_by_email
from exceptions import InvalidTokenError, TokenExpiredError


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


def authenticate_user(email: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_email(email=email, db=db)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Type[User]:
    try:
        payload = decode_access_token(token)
        user = get_user_by_email(email=payload["email"], db=db)
        if not user:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_MESSAGE
        )
    except (TokenExpiredError, InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_MESSAGE
        )
    else:
        return user
