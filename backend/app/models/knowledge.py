from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class KnowledgeBaseUpdate(BaseModel):
    """知识库更新请求"""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""

    id: int
    expert_id: int
    name: str
    description: Optional[str] = None
    created_time: datetime
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class KnowledgeItemCreate(BaseModel):
    """知识条目创建请求"""

    title: str = Field(..., max_length=200)
    content: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    enabled: bool = True


class KnowledgeItemUpdate(BaseModel):
    """知识条目更新请求"""

    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class KnowledgeItemResponse(BaseModel):
    """知识条目响应"""

    id: int
    knowledge_base_id: int
    title: str
    content: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    enabled: bool
    created_time: datetime
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True
