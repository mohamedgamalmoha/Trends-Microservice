from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime

from app.db.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, index=True)
    username = Column(String(200), unique=True, index=True)
    first_name = Column(String(200))
    last_name = Column(String(225))
    phone_number = Column(String(225))
    hashed_password = Column(String(225))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    date_created = Column(DateTime, default=datetime.utcnow)
