from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SkillBaseUpdate(BaseModel):
    """技能库更新请求"""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class SkillBaseResponse(BaseModel):
    """技能库响应"""

    id: int
    expert_id: int
    name: str
    description: Optional[str] = None
    created_time: datetime
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class SkillItemCreate(BaseModel):
    """技能条目创建请求"""

    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    content: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: List[str] = []
    enabled: bool = True


class SkillItemUpdate(BaseModel):
    """技能条目更新请求"""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    enabled: Optional[bool] = None


class SkillItemResponse(BaseModel):
    """技能条目响应"""

    id: int
    skill_base_id: int
    name: str
    description: Optional[str] = None
    content: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    enabled: bool
    created_time: datetime
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True
