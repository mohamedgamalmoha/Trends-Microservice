from datetime import datetime

from sqlalchemy import Column, Float, Integer, String, DateTime, JSON, Enum
from shared_utils.schemas.status import TaskStatus

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(String, index=True, primary_key=True)
    user_id = Column(Integer, index=True)
    search_task_id = Column(String, index=True, nullable=True)
    question = Column(String(500), nullable=False)
    context = Column(String(2000), nullable=True)
    temperature = Column(Float, default=0.7, nullable=True)
    max_tokens = Column(Integer, default=250, nullable=True)
    schedule_at = Column(DateTime, default=datetime.now, nullable=True)

    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    result_data = Column(JSON, nullable=True)
    error = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
