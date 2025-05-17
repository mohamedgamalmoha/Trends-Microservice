import os
from typing import Optional

import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv('../../.env')


class Settings(BaseSettings):
    SERVICE_BASE_URL: Optional[str] = os.environ.get('SERVICE_BASE_URL', None)

    USER_SERVICE_CREATE_PATH: Optional[str] =  os.environ.get('USER_SERVICE_CREATE_PATH', None)
    USER_SERVICE_AUTH_PATH: Optional[str] =  os.environ.get('USER_SERVICE_AUTH_PATH', None)
    USER_SERVICE_AUTH_TOKEN_IDENTIFIER: Optional[str] =  os.environ.get('USER_SERVICE_AUTH_TOKEN_IDENTIFIER', "token")

    TRENDS_SERVICE_PATH: Optional[str] = os.environ.get('TRENDS_SERVICE_PATH', None)
    THINK_SERVICE_PATH: Optional[str] = os.environ.get('THINK_SERVICE_PATH', None)

    MIN_WAITING_TIME: Optional[int] = os.environ.get('MIN_WAITING_TIME', 1)
    MAX_WAITING_TIME: Optional[int] = os.environ.get('MAX_WAITING_TIME', 5)

    class Config:
        frozen = True
        case_sensitive = True


settings = Settings()
