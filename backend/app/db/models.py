from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from app.core.database import Base


# 权限关联表
user_expert_permission = Table(
    'user_expert_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('expert_id', Integer, ForeignKey('ai_experts.id'), primary_key=True)
)

user_subagent_permission = Table(
    'user_subagent_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('subagent_id', Integer, ForeignKey('expert_sub_agents.id'), primary_key=True)
)

user_mcp_permission = Table(
    'user_mcp_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('mcp_id', Integer, ForeignKey('mcp_tools.id'), primary_key=True)
)

user_skill_permission = Table(
    'user_skill_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('expert_skill_items.id'), primary_key=True)
)

user_knowledge_permission = Table(
    'user_knowledge_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('knowledge_id', Integer, ForeignKey('expert_knowledge_items.id'), primary_key=True)
)


class UserORM(Base):
    """用户表"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    email = Column(String(100), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=True)
    real_name = Column(String(100), nullable=True)
    role = Column(String(20), nullable=False, default="user")  # admin/user
    status = Column(String(20), nullable=False, default="active")  # active/inactive
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    # 权限关系
    permitted_experts = relationship("AIExpertORM", secondary=user_expert_permission, back_populates="permitted_users")
    permitted_subagents = relationship("SubAgentORM", secondary=user_subagent_permission, back_populates="permitted_users")
    permitted_mcps = relationship("MCPToolORM", secondary=user_mcp_permission, back_populates="permitted_users")
    permitted_skills = relationship("SkillItemORM", secondary=user_skill_permission, back_populates="permitted_users")
    permitted_knowledge = relationship("KnowledgeItemORM", secondary=user_knowledge_permission, back_populates="permitted_users")


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
    created_by = Column(String(50), nullable=False, default="admin")
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_by = Column(String(50), nullable=True)
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    knowledge_base = relationship("KnowledgeBaseORM", back_populates="expert", uselist=False, cascade="all, delete-orphan")
    skill_base = relationship("SkillBaseORM", back_populates="expert", uselist=False, cascade="all, delete-orphan")
    knowledge_graphs = relationship("KnowledgeGraphORM", back_populates="expert", cascade="all, delete-orphan")
    permitted_users = relationship("UserORM", secondary=user_expert_permission, back_populates="permitted_experts")


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
    file_path = Column(String(500), nullable=True)  # 文件路径
    file_name = Column(String(200), nullable=True)  # 文件名
    metadata_json = Column("metadata", JSON, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    knowledge_base = relationship("KnowledgeBaseORM", back_populates="items")
    permitted_users = relationship("UserORM", secondary=user_knowledge_permission, back_populates="permitted_knowledge")


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
    file_path = Column(String(500), nullable=True)  # 文件路径
    file_name = Column(String(200), nullable=True)  # 文件名
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    enabled = Column(Boolean, nullable=False, default=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    skill_base = relationship("SkillBaseORM", back_populates="items")
    permitted_users = relationship("UserORM", secondary=user_skill_permission, back_populates="permitted_skills")


class SubAgentORM(Base):
    """专家子智能体"""

    __tablename__ = "expert_sub_agents"

    id = Column(Integer, primary_key=True, index=True)
    expert_id = Column(Integer, ForeignKey("ai_experts.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)
    api_key = Column(String(500), nullable=True)  # API密钥（可选）
    status = Column(String(20), nullable=False, default="draft")
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    expert = relationship("AIExpertORM")
    permitted_users = relationship("UserORM", secondary=user_subagent_permission, back_populates="permitted_subagents")


class KnowledgeGraphORM(Base):
    """知识图谱"""

    __tablename__ = "knowledge_graphs"

    id = Column(Integer, primary_key=True, index=True)
    expert_id = Column(Integer, ForeignKey("ai_experts.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    graph_type = Column(String(50), nullable=False, default="general")  # general/domain/custom
    storage = Column(String(50), nullable=False, default="neo4j")  # neo4j/memory
    file_path = Column(String(500), nullable=True)  # 文件路径
    file_name = Column(String(200), nullable=True)  # 文件名
    node_count = Column(Integer, nullable=False, default=0)
    edge_count = Column(Integer, nullable=False, default=0)
    config = Column(JSON, nullable=True)  # 存储图谱配置
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    expert = relationship("AIExpertORM", back_populates="knowledge_graphs")


class MCPToolORM(Base):
    """MCP工具"""

    __tablename__ = "mcp_tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    icon = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    tool_type = Column(String(50), nullable=False)  # function/api/integration
    method = Column(String(20), nullable=True)  # GET/POST/PUT/DELETE
    endpoint = Column(String(500), nullable=True)
    config = Column(JSON, nullable=True)  # 工具配置
    enabled = Column(Boolean, nullable=False, default=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    permitted_users = relationship("UserORM", secondary=user_mcp_permission, back_populates="permitted_mcps")


class ModelConfigORM(Base):
    """模型配置"""

    __tablename__ = "model_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # openai/anthropic/ollama/custom
    model_name = Column(String(100), nullable=False)
    api_key = Column(String(500), nullable=True)
    base_url = Column(String(500), nullable=True)
    temperature = Column(Integer, nullable=False, default=70)  # 0-100
    max_tokens = Column(Integer, nullable=True)
    config = Column(JSON, nullable=True)  # 其他配置
    enabled = Column(Boolean, nullable=False, default=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

