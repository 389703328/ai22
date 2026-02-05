"""
User schemas for request/response validation
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema"""

    username: str
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    """User creation schema"""

    password: str


class UserUpdate(BaseModel):
    """User update schema"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema"""

    username: str
    password: str


class Token(BaseModel):
    """Token response schema"""

    access_token: str
    token_type: str = "bearer"
