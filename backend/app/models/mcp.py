from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MCPToolBase(BaseModel):
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    tool_type: str
    method: Optional[str] = None
    endpoint: Optional[str] = None
    config: Optional[dict] = None
    enabled: bool = True


class MCPToolCreate(MCPToolBase):
    pass


class MCPToolUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    tool_type: Optional[str] = None
    method: Optional[str] = None
    endpoint: Optional[str] = None
    config: Optional[dict] = None
    enabled: Optional[bool] = None


class MCPToolResponse(MCPToolBase):
    id: int
    created_time: datetime
    updated_time: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MCPToolListResponse(BaseModel):
    total: int
    items: list[MCPToolResponse]
    page: int
    page_size: int
