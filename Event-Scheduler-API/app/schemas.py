from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# Event schemas
class EventBase(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime

class EventCreate(EventBase):
    location: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[dict] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[dict] = None

class EventOut(EventBase):
    id: int
    location: Optional[str]
    is_recurring: bool
    recurrence_pattern: Optional[dict]
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BatchEventCreate(BaseModel):
    events: List[EventCreate]

# Permission schemas
class PermissionBase(BaseModel):
    user_id: int
    role: str

class PermissionCreate(PermissionBase):
    pass

class PermissionOut(PermissionBase):
    id: int
    granted_at: datetime

    class Config:
        orm_mode = True

# History schemas
class ChangeBase(BaseModel):
    version: int
    change_type: str
    changes: dict
    changed_at: datetime
    user_id: int

class ChangeOut(ChangeBase):
    id: int

    class Config:
        orm_mode = True

class DiffOut(BaseModel):
    version1: int
    version2: int
    differences: dict