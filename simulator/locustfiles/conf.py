import os
from typing import Optional

import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv('../.env')


class Settings(BaseSettings):
    USER_SERVICE_URL: Optional[str] = os.environ.get('USER_SERVICE_URL', None)
    MIN_WAITING_TIME: Optional[int] = os.environ.get('MIN_WAITING_TIME', 1)
    MAX_WAITING_TIME: Optional[int] = os.environ.get('MAX_WAITING_TIME', 5)

    class Config:
        frozen = True
        case_sensitive = True


settings = Settings()
