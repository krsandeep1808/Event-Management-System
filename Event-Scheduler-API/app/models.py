from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum
from datetime import datetime

class UserRole(str, PyEnum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    permissions = relationship("EventPermission", back_populates="user")
    changes = relationship("EventChange", back_populates="user")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String, nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    permissions = relationship("EventPermission", back_populates="event")
    changes = relationship("EventChange", back_populates="event")

class EventPermission(Base):
    __tablename__ = "event_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    granted_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="permissions")
    event = relationship("Event", back_populates="permissions")

class EventChange(Base):
    __tablename__ = "event_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    version = Column(Integer)
    change_type = Column(String)  # 'create', 'update', 'delete', 'permission_change'
    changes = Column(JSON)  # Stores the diff
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="changes")
    event = relationship("Event", back_populates="changes")