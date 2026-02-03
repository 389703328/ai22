from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SubAgentBase(BaseModel):
    """子智能体基础模型"""

    name: str = Field(..., max_length=200, description="子智能体名称")
    description: Optional[str] = Field(None, description="子智能体描述")
    prompt: str = Field(..., description="子智能体提示词")
    api_key: Optional[str] = Field(None, description="API密钥（可选）")
    status: str = Field("draft", max_length=20, description="状态: active, inactive, draft")


class SubAgentCreate(SubAgentBase):
    """创建子智能体请求"""


class SubAgentUpdate(BaseModel):
    """更新子智能体请求"""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    prompt: Optional[str] = None
    api_key: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)


class SubAgentResponse(SubAgentBase):
    """子智能体响应"""

    id: int
    expert_id: int
    created_time: datetime
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubAgentListResponse(BaseModel):
    """子智能体列表响应"""

    total: int
    items: list[SubAgentResponse]
