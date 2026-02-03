from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from app.core.database import Base


class AIExpertORM(Base):
    """AI专家数据库模型"""

    __tablename__ = "ai_experts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    avatar = Column(String(500), nullable=True)
    welcome_message = Column(String(500), nullable=True)
    introduction = Column(Text, nullable=True)
    capabilities = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    version = Column(String(50), nullable=False, default="1.0.0")
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    sort_order = Column(Integer, nullable=False, default=999)
    usage_count = Column(Integer, nullable=False, default=0)
    created_by = Column(String(50), nullable=False)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_by = Column(String(50), nullable=True)
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    knowledge_base = relationship("KnowledgeBaseORM", back_populates="expert", uselist=False)
    skill_base = relationship("SkillBaseORM", back_populates="expert", uselist=False)


class KnowledgeBaseORM(Base):
    """专家知识库"""

    __tablename__ = "expert_knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    expert_id = Column(Integer, ForeignKey("ai_experts.id"), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    expert = relationship("AIExpertORM", back_populates="knowledge_base")
    items = relationship("KnowledgeItemORM", back_populates="knowledge_base", cascade="all, delete-orphan")


class KnowledgeItemORM(Base):
    """知识库条目"""

    __tablename__ = "expert_knowledge_items"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("expert_knowledge_bases.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    knowledge_base = relationship("KnowledgeBaseORM", back_populates="items")


class SkillBaseORM(Base):
    """专家技能库"""

    __tablename__ = "expert_skill_bases"

    id = Column(Integer, primary_key=True, index=True)
    expert_id = Column(Integer, ForeignKey("ai_experts.id"), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    expert = relationship("AIExpertORM", back_populates="skill_base")
    items = relationship("SkillItemORM", back_populates="skill_base", cascade="all, delete-orphan")


class SkillItemORM(Base):
    """技能库条目"""

    __tablename__ = "expert_skill_items"

    id = Column(Integer, primary_key=True, index=True)
    skill_base_id = Column(Integer, ForeignKey("expert_skill_bases.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    enabled = Column(Boolean, nullable=False, default=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    skill_base = relationship("SkillBaseORM", back_populates="items")


class SubAgentORM(Base):
    """专家子智能体"""

    __tablename__ = "expert_sub_agents"

    id = Column(Integer, primary_key=True, index=True)
    expert_id = Column(Integer, ForeignKey("ai_experts.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    expert = relationship("AIExpertORM")
