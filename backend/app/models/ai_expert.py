from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AIExpertBase(BaseModel):
    """AI专家基础模型"""
    code: str = Field(..., max_length=50, description="专家唯一编码")
    name: str = Field(..., max_length=100, description="专家名称")
    avatar: Optional[str] = Field(None, max_length=500, description="头像URL")
    welcome_message: Optional[str] = Field("欢迎咨询！", max_length=500, description="欢迎语")
    introduction: Optional[str] = Field(None, description="专家介绍")
    capabilities: Optional[str] = Field(None, description="功能介绍")
    prompt: str = Field(..., description="核心提示词")
    status: str = Field("draft", max_length=20, description="状态: active, inactive, draft")
    version: str = Field("1.0.0", max_length=50, description="版本号")
    category: Optional[str] = Field(None, max_length=100, description="分类")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    sort_order: Optional[int] = Field(999, description="排序权重")


class AIExpertCreate(AIExpertBase):
    """创建AI专家请求"""
    created_by: str = Field(..., max_length=50, description="创建人")


class AIExpertUpdate(BaseModel):
    """更新AI专家请求"""
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    avatar: Optional[str] = Field(None, max_length=500)
    welcome_message: Optional[str] = Field(None, max_length=500)
    introduction: Optional[str] = None
    capabilities: Optional[str] = None
    prompt: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)
    version: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    sort_order: Optional[int] = None
    updated_by: Optional[str] = Field(None, max_length=50)


class AIExpertResponse(AIExpertBase):
    """AI专家响应"""
    id: int
    usage_count: int = 0
    created_by: str
    created_time: datetime
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIExpertListResponse(BaseModel):
    """分页列表响应"""
    total: int
    items: List[AIExpertResponse]
    page: int
    page_size: int
