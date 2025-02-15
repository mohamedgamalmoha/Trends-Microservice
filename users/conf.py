import os
import logging
from typing import ClassVar

import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: ClassVar[str]= os.environ.get('SQLALCHEMY_DATABASE_URL')


settings = Settings()
