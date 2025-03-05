from datetime import datetime
from typing import Dict, Optional, Any

import pydantic

from app.models.task import TaskStatus
from app.schemas.query import TrendsQuery


class TaskCreate(pydantic.BaseModel):
    user_id: int
    schedule_at: Optional[datetime] = pydantic.Field(default_factory=datetime.now)
    request_data: TrendsQuery

    class Config:
        from_attributes=True


class TaskRetrieve(pydantic.BaseModel):
    task_id: str
    user_id: int
    status: TaskStatus
    request_data: Optional[TrendsQuery] = None
    schedule_at: datetime
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes=True


class TaskUpdate(pydantic.BaseModel):
    status: Optional[TaskStatus] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes=True
