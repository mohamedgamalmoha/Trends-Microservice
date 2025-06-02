import os
from typing import Optional

import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv('../../.env')


class Settings(BaseSettings):
    # General
    SERVICE_NAME: Optional[str] = os.environ.get('SERVICE_NAME', None)
    SERVICE_VERSION: Optional[str] = os.environ.get('SERVICE_VERSION', None)

    # Database Envs
    SQLALCHEMY_DATABASE_URL: Optional[str] = os.environ.get('SQLALCHEMY_DATABASE_URL', None)

    # Password Envs
    PASSWORD_CRYPT_CONTEXT_SCHEMA: Optional[str] = os.environ.get("PASSWORD_CRYPT_CONTEXT_SCHEMA", None)

    # Access Token Envs
    ACCESS_TOKEN_SECRET_KEY: Optional[str] = os.environ.get("ACCESS_TOKEN_SECRET_KEY", None)
    ACCESS_TOKEN_ALGORITHM: Optional[str] = os.environ.get("ACCESS_TOKEN_ALGORITHM", None)
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", None)

    # Verification Token Envs
    VERIFICATION_TOKEN_SECRET_KEY: Optional[str] = os.environ.get("VERIFICATION_TOKEN_SECRET_KEY", None)
    VERIFICATION_TOKEN_ALGORITHM: Optional[str] = os.environ.get("VERIFICATION_TOKEN_ALGORITHM", None)
    VERIFICATION_TOKEN_EXPIRE_MINUTES: Optional[int] = os.environ.get("VERIFICATION_TOKEN_EXPIRE_MINUTES", None)

    # Password Reset Token Envs
    PASSWORD_REST_TOKEN_SECRET_KEY: Optional[str] = os.environ.get("PASSWORD_REST_TOKEN_SECRET_KEY", None)
    PASSWORD_REST_TOKEN_ALGORITHM: Optional[str] = os.environ.get("PASSWORD_REST_TOKEN_ALGORITHM", None)
    PASSWORD_REST_TOKEN_EXPIRE_MINUTES: Optional[int] = os.environ.get("PASSWORD_REST_TOKEN_EXPIRE_MINUTES", None)

    # OpenTelemetry Envs
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", None)
    OTEL_EXPORTER_OTLP_INSECURE: Optional[bool] = os.environ.get("OTEL_EXPORTER_OTLP_INSECURE", None)

    class Config:
        frozen = True
        case_sensitive = True


settings = Settings()
