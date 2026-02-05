from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class QuestionBaseUpdate(BaseModel):
    """问题库更新请求"""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class QuestionBaseResponse(BaseModel):
    """问题库响应"""

    id: int
    expert_id: int
    name: str
    description: Optional[str] = None
    created_time: datetime
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuestionItemCreate(BaseModel):
    """问题条目创建请求"""

    question: str
    answer: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: List[str] = []
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    enabled: bool = True


class QuestionItemUpdate(BaseModel):
    """问题条目更新请求"""

    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    enabled: Optional[bool] = None


class QuestionItemResponse(BaseModel):
    """问题条目响应"""

    id: int
    question_base_id: int
    question: str
    answer: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    difficulty: Optional[int] = None
    enabled: bool
    created_time: datetime
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True
