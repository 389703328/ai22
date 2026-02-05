from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    role: str = "user"
    status: str = "active"


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError('密码不能为空')
        if len(v) < 6:
            raise ValueError('密码长度不能少于 6 个字符')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('密码长度不能超过 72 字节')
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) < 6:
            raise ValueError('密码长度不能少于 6 个字符')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('密码长度不能超过 72 字节')
        return v

        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    role: str
    status: str
    created_time: datetime
    updated_time: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    total: int
    items: list[UserResponse]
    page: int
    page_size: int


class UserPermissionUpdate(BaseModel):
    expert_ids: Optional[list[int]] = None
    subagent_ids: Optional[list[int]] = None
    mcp_ids: Optional[list[int]] = None
    skill_ids: Optional[list[int]] = None
    knowledge_ids: Optional[list[int]] = None
    model_ids: Optional[list[int]] = None
    knowledge_graph_ids: Optional[list[int]] = None

