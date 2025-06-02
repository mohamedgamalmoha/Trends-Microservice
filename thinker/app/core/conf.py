import os
from typing import Optional

import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv('../../.env')


class Settings(BaseSettings):
    # General
    SERVICE_NAME: str = os.environ.get('SERVICE_NAME', None)
    SERVICE_VERSION: str = os.environ.get('SERVICE_VERSION', None)

    # Database Envs
    SQLALCHEMY_DATABASE_URL: Optional[str] = os.environ.get('SQLALCHEMY_DATABASE_URL', None)
   
    USER_AUTH_URL: Optional[str] = os.environ.get('USER_AUTH_URL', None)
    USER_INFO_URL: Optional[str] = os.environ.get('USER_INFO_URL', None)
   
    OLLAMA_API_URL: Optional[str] = os.environ.get('OLLAMA_API_URL', None)
    OLLAMA_MODEL_NAME: Optional[str] = os.environ.get('OLLAMA_MODEL_NAME', None)
    OLLAMA_REQUEST_TIMEOUT: int = os.environ.get('OLLAMA_REQUEST_TIMEOUT', None)

    CELERY_BROKER_URL: Optional[str] = os.environ.get('CELERY_BROKER_URL', None)
    CELERY_RESULT_BACKEND: Optional[str] = os.environ.get('CELERY_RESULT_BACKEND', None)

    TASK_CALLBACK_URL: Optional[str] = os.environ.get('TASK_CALLBACK_URL', None)
    TASK_SIGNATURE_KEY: Optional[str] = os.environ.get('TASK_SIGNATURE_KEY', None)

    # OpenTelemetry Envs
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", None)
    OTEL_EXPORTER_OTLP_INSECURE: Optional[bool] = os.environ.get("OTEL_EXPORTER_OTLP_INSECURE", None)

    class Config:
        frozen = True
        case_sensitive = True


settings = Settings()
