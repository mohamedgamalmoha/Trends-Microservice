import os
import logging

import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv('../../.env')

logging.basicConfig(level=logging.INFO)


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str= os.environ.get('SQLALCHEMY_DATABASE_URL')
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    ACCESS_TOKEN_ALGORITHM: str = os.environ.get("ACCESS_TOKEN_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
    PASSWORD_CRYPT_CONTEXT_SCHEMA: str = os.environ.get("PASSWORD_CRYPT_CONTEXT_SCHEMA")


settings = Settings()
