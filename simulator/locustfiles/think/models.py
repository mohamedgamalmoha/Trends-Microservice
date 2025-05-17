import uuid
from typing import Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Think:
    task_id: uuid.UUID
    user_id: int
    search_task_id: Optional[uuid.UUID]
    question: str
    context: str
    temperature: float
    max_tokens: int
    status: str
    result_data: dict
    error: dict
    retry_count: int
    schedule_at: datetime
    created_at: datetime
    updated_at: datetime
