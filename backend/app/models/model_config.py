from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ModelConfigBase(BaseModel):
    name: str
    provider: str
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: int = 70
    max_tokens: Optional[int] = None
    config: Optional[dict] = None
    enabled: bool = True


class ModelConfigCreate(ModelConfigBase):
    pass


class ModelConfigUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: Optional[int] = None
    max_tokens: Optional[int] = None
    config: Optional[dict] = None
    enabled: Optional[bool] = None


class ModelConfigResponse(ModelConfigBase):
    id: int
    created_time: datetime
    updated_time: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ModelConfigListResponse(BaseModel):
    total: int
    items: list[ModelConfigResponse]
    page: int
    page_size: int
