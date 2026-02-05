from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SubAgentSessionCreate(BaseModel):
    """子智能体会话创建请求"""

    user_id: int = Field(..., description="用户ID")
    session_id: Optional[str] = Field(None, max_length=100, description="会话唯一ID")
    title: Optional[str] = Field(None, max_length=200, description="会话标题")
    content: Optional[str] = Field(None, description="会话内容")
    feedback_type: str = Field("none", pattern="^(none|like|dislike)$", description="点赞/踩")
    comment: Optional[str] = Field(None, description="用户评论")


class SubAgentSessionUpdate(BaseModel):
    """子智能体会话更新请求"""

    session_id: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    feedback_type: Optional[str] = Field(None, pattern="^(none|like|dislike)$")
    comment: Optional[str] = None


class SubAgentSessionResponse(BaseModel):
    """子智能体会话响应"""

    id: int
    sub_agent_id: int
    user_id: int
    session_id: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    feedback_type: str
    comment: Optional[str] = None
    created_time: datetime
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubAgentSessionListResponse(BaseModel):
    """子智能体会话列表响应"""

    total: int
    items: list[SubAgentSessionResponse]
