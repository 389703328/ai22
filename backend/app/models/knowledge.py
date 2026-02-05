from pydantic import BaseModel, Field, model_validator
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

    name: str = Field(..., max_length=200)
    text: Optional[str] = None
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    sub_agent_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    indexing_technique: Optional[str] = None
    doc_form: Optional[str] = None
    doc_language: Optional[str] = None
    process_rule: Optional[Dict[str, Any]] = None
    retrieval_model: Optional[Dict[str, Any]] = None
    embedding_model: Optional[str] = None
    embedding_model_provider: Optional[str] = None
    enabled: bool = True

    @model_validator(mode="after")
    def validate_content_or_file(self):
        has_text = bool(self.text) or bool(self.content)
        has_file = bool(self.file_path) or bool(self.file_name)
        if not has_text and not has_file:
            raise ValueError("请提供文档内容或上传文件")
        return self


class KnowledgeItemUpdate(BaseModel):
    """知识条目更新请求"""

    name: Optional[str] = Field(None, max_length=200)
    text: Optional[str] = None
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    sub_agent_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    indexing_technique: Optional[str] = None
    doc_form: Optional[str] = None
    doc_language: Optional[str] = None
    process_rule: Optional[Dict[str, Any]] = None
    retrieval_model: Optional[Dict[str, Any]] = None
    embedding_model: Optional[str] = None
    embedding_model_provider: Optional[str] = None
    enabled: Optional[bool] = None


class KnowledgeItemResponse(BaseModel):
    """知识条目响应"""

    id: int
    knowledge_base_id: int
    name: str
    text: Optional[str] = None
    title: str
    content: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    sub_agent_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    indexing_technique: Optional[str] = None
    doc_form: Optional[str] = None
    doc_language: Optional[str] = None
    process_rule: Optional[Dict[str, Any]] = None
    retrieval_model: Optional[Dict[str, Any]] = None
    embedding_model: Optional[str] = None
    embedding_model_provider: Optional[str] = None
    enabled: bool
    created_time: datetime
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True
