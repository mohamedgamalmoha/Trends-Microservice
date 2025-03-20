from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from shared_utils.db.base import Base
from shared_utils.schemas.status import TaskStatus


class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(String, index=True, primary_key=True)
    user_id = Column(Integer, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    request_data = Column(JSON)
    schedule_at = Column(DateTime, default=datetime.now)

    result_data = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
