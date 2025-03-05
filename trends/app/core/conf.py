import os
import logging

import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv('../../.env')

logging.basicConfig(level=logging.INFO)


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str= os.environ.get('SQLALCHEMY_DATABASE_URL')
    CELERY_BROKER_URL: str = os.environ.get('SQLALCHEMY_DATABASE_URL')
    CELERY_RESULT_BACKEND: str = os.environ.get('CELERY_RESULT_BACKEND')


settings = Settings()
