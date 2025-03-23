import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from shared_utils.db.base import Base
from shared_utils.schemas.status import TaskStatus


class PropertyEnum(enum.Enum):
    WEB_SEARCH = "web"
    YOUTUBE_SEARCH = "youtube"
    NEWS_SEARCH = "news"
    IMAGE_SEARCH = "images"
    FROOGLE_SEARCH = "froogle"


class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(String, index=True, primary_key=True)
    user_id = Column(Integer, index=True)
    q = Column(JSON)
    geo = Column(String)
    time = Column(String, nullable=True)
    cat = Column(Integer, default=0)
    gprop = Column(Enum(PropertyEnum), default=PropertyEnum.WEB_SEARCH)
    tz = Column(Integer, default=0)
    schedule_at = Column(DateTime, default=datetime.now)

    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    result_data = Column(JSON, nullable=True)
    error = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
