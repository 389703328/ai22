from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class KnowledgeGraphBase(BaseModel):
    name: str
    description: Optional[str] = None
    graph_type: str = "general"
    storage: str = "neo4j"
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    config: Optional[dict] = None


class KnowledgeGraphCreate(KnowledgeGraphBase):
    expert_id: int


class KnowledgeGraphUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    graph_type: Optional[str] = None
    storage: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    config: Optional[dict] = None


class KnowledgeGraphResponse(KnowledgeGraphBase):
    id: int
    expert_id: int
    node_count: int
    edge_count: int
    created_time: datetime
    updated_time: Optional[datetime] = None

    model_config = {"from_attributes": True}


class KnowledgeGraphListResponse(BaseModel):
    total: int
    items: list[KnowledgeGraphResponse]
