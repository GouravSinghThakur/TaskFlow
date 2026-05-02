from datetime import datetime
import enum

from sqlalchemy import Column, DateTime, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    projects_created = relationship("Project", back_populates="created_by_user", foreign_keys="Project.created_by")
    tasks_created = relationship("Task", back_populates="created_by_user", foreign_keys="Task.created_by")
    tasks_assigned = relationship("Task", back_populates="assigned_to_user", foreign_keys="Task.assigned_to")
