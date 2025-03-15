import enum

import pydantic


class HealthStatusEnum(enum.Enum):
    OK = "Ok"
    ERROR = "Error"
    WARNING = "Warning"


class Health(pydantic.BaseModel):
    status: HealthStatusEnum
    message: str
