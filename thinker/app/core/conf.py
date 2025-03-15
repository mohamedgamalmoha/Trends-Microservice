import os

import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv('../../.env')


class Settings(BaseSettings):
    OLLAMA_API_URL: str = os.environ.get('OLLAMA_API_URL')
    OLLAMA_MODEL_NAME: str = os.environ.get('OLLAMA_MODEL_NAME')
    OLLAMA_REQUEST_TIMEOUT: int = os.environ.get('OLLAMA_REQUEST_TIMEOUT')


settings = Settings()
