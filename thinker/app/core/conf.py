import os

import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv('../../.env')


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = os.environ.get('SQLALCHEMY_DATABASE_URL')
   
    USER_AUTH_URL: str = os.environ.get('USER_AUTH_URL')
    USER_INFO_URL: str = os.environ.get('USER_INFO_URL')
   
    OLLAMA_API_URL: str = os.environ.get('OLLAMA_API_URL')
    OLLAMA_MODEL_NAME: str = os.environ.get('OLLAMA_MODEL_NAME')
    OLLAMA_REQUEST_TIMEOUT: int = os.environ.get('OLLAMA_REQUEST_TIMEOUT')

    CELERY_BROKER_URL: str = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND: str = os.environ.get('CELERY_RESULT_BACKEND')


settings = Settings()
