import os
import logging

import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv('../../.env')

logging.basicConfig(level=logging.INFO)


class Settings(BaseSettings):
    # General
    SQLALCHEMY_DATABASE_URL: str= os.environ.get('SQLALCHEMY_DATABASE_URL')

    # Password Envs
    PASSWORD_CRYPT_CONTEXT_SCHEMA: str = os.environ.get("PASSWORD_CRYPT_CONTEXT_SCHEMA")

    # Access Token Envs
    ACCESS_TOKEN_SECRET_KEY: str = os.environ.get("ACCESS_TOKEN_SECRET_KEY")
    ACCESS_TOKEN_ALGORITHM: str = os.environ.get("ACCESS_TOKEN_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")

    # Verification Token Envs
    VERIFICATION_TOKEN_SECRET_KEY: str = os.environ.get("VERIFICATION_TOKEN_SECRET_KEY")
    VERIFICATION_TOKEN_ALGORITHM: str = os.environ.get("VERIFICATION_TOKEN_ALGORITHM")
    VERIFICATION_TOKEN_EXPIRE_MINUTES: int = os.environ.get("VERIFICATION_TOKEN_EXPIRE_MINUTES")

    # Password Reset Token Envs
    PASSWORD_REST_TOKEN_SECRET_KEY: str = os.environ.get("PASSWORD_REST_TOKEN_SECRET_KEY")
    PASSWORD_REST_TOKEN_ALGORITHM: str = os.environ.get("PASSWORD_REST_TOKEN_ALGORITHM")
    PASSWORD_REST_TOKEN_EXPIRE_MINUTES: int = os.environ.get("PASSWORD_REST_TOKEN_EXPIRE_MINUTES")


settings = Settings()
