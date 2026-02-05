from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from app.core.database import Base



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

    resource_permissions = relationship(
        "UserResourcePermissionORM",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserResourcePermissionORM(Base):
    """统一资源权限表"""

    __tablename__ = "user_resource_permissions"
    __table_args__ = (
        UniqueConstraint("user_id", "resource_type", "resource_id", name="uniq_user_resource_permission"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(Integer, nullable=False, index=True)
    permission_level = Column(String(20), nullable=False, default="read")
    granted_by = Column(String(50), nullable=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("UserORM", back_populates="resource_permissions")


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
    question_base = relationship("QuestionBaseORM", back_populates="expert", uselist=False, cascade="all, delete-orphan")
    knowledge_graphs = relationship("KnowledgeGraphORM", back_populates="expert", cascade="all, delete-orphan")


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
    sub_agent_id = Column(Integer, ForeignKey("expert_sub_agents.id"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    name = Column(String(200), nullable=False)
    text = Column(Text, nullable=True)
    indexing_technique = Column(String(50), nullable=True)
    doc_form = Column(String(50), nullable=True)
    doc_language = Column(String(50), nullable=True)
    process_rule = Column(JSON, nullable=True)
    retrieval_model = Column(JSON, nullable=True)
    embedding_model = Column(String(100), nullable=True)
    embedding_model_provider = Column(String(100), nullable=True)
    file_path = Column(String(500), nullable=True)  # 文件路径
    file_name = Column(String(200), nullable=True)  # 文件名
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
    file_path = Column(String(500), nullable=True)  # 文件路径
    file_name = Column(String(200), nullable=True)  # 文件名
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    enabled = Column(Boolean, nullable=False, default=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    skill_base = relationship("SkillBaseORM", back_populates="items")


class QuestionBaseORM(Base):
    """专家问题库"""

    __tablename__ = "expert_question_bases"

    id = Column(Integer, primary_key=True, index=True)
    expert_id = Column(Integer, ForeignKey("ai_experts.id"), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    expert = relationship("AIExpertORM", back_populates="question_base")
    items = relationship("QuestionItemORM", back_populates="question_base", cascade="all, delete-orphan")


class QuestionItemORM(Base):
    """问题库条目"""

    __tablename__ = "expert_question_items"

    id = Column(Integer, primary_key=True, index=True)
    question_base_id = Column(Integer, ForeignKey("expert_question_bases.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    difficulty = Column(Integer, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    question_base = relationship("QuestionBaseORM", back_populates="items")


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
    sessions = relationship("SubAgentSessionORM", back_populates="sub_agent", cascade="all, delete-orphan")


class SubAgentSessionORM(Base):
    """子智能体会话库"""

    __tablename__ = "sub_agent_sessions"

    id = Column(Integer, primary_key=True, index=True)
    sub_agent_id = Column(Integer, ForeignKey("expert_sub_agents.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)
    feedback_type = Column(String(20), nullable=False, default="none")
    comment = Column(Text, nullable=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=True, onupdate=func.now())

    sub_agent = relationship("SubAgentORM", back_populates="sessions")
    user = relationship("UserORM")


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

