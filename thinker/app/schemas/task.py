from typing import Optional
from datetime import datetime

import pydantic

from app.core.conf import settings
from app.models.task import TaskStatus


class TaskCreate(pydantic.BaseModel):
    user_id: int
    search_task_id: Optional[str] = None
    question: str = pydantic.Field(
        ...,
        min_length=3,
        max_length=500,
        description="The question to be answered (3-500 characters)"
    )
    context: Optional[str] = pydantic.Field(
        None,
        max_length=2000,
        description="Optional context to provide background information for the question"
    )
    temperature: Optional[float] = pydantic.Field(
        0.7,
        ge=0.0,
        le=2.0,
        description="Controls randomness in generation. Lower = more deterministic (0.0-2.0)"
    )
    max_tokens: Optional[int] = pydantic.Field(
        250,
        ge=10,
        le=512,
        description="Maximum number of output tokens to generate (10-512)"
    )
    schedule_at: Optional[datetime] = pydantic.Field(default_factory=datetime.now)

    class Config:
        from_attributes=True


class ThinkResponse(pydantic.BaseModel):
    answer: str
    thinking: str

    class Config:
        from_attributes=True


class ThinkError(pydantic.BaseModel):
    code: int
    error: str

    class Config:
        from_attributes=True


class TaskRetrieve(TaskCreate):
    task_id: str

    status: TaskStatus

    result_data: Optional[ThinkResponse] = None
    error: Optional[ThinkError] = None
    retry_count: Optional[int] = 0

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes=True
