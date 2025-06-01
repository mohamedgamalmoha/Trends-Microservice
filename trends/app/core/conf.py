import os
from typing import Optional

import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv('../../.env')


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: Optional[str] = os.environ.get('SQLALCHEMY_DATABASE_URL', None)
    
    CELERY_BROKER_URL: Optional[str] = os.environ.get('SQLALCHEMY_DATABASE_URL', None)
    CELERY_RESULT_BACKEND: Optional[str] = os.environ.get('CELERY_RESULT_BACKEND', None)
    
    USER_AUTH_URL: Optional[str] = os.environ.get('USER_AUTH_URL', None)

    TASK_CALLBACK_URL: Optional[str] = os.environ.get('TASK_CALLBACK_URL', None)
    TASK_SIGNATURE_KEY: Optional[str] = os.environ.get('TASK_SIGNATURE_KEY', None)

    class Config:
        frozen = True
        case_sensitive = True


settings = Settings()
