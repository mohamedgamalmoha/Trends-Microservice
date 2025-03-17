import pydantic


class Health(pydantic.BaseModel):
    message: str
