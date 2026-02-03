from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.db.models import AIExpertORM, KnowledgeBaseORM, SkillBaseORM, SubAgentORM
from app.models.ai_expert import (
    AIExpertCreate,
    AIExpertUpdate,
    AIExpertResponse,
    AIExpertListResponse,
)
from app.models.sub_agent import (
    SubAgentCreate,
    SubAgentUpdate,
    SubAgentResponse,
    SubAgentListResponse,
)

router = APIRouter()


class AIRequest(BaseModel):
    prompt: str


class AIResponse(BaseModel):
    response: str


@router.post("/chat", response_model=AIResponse)
async def chat_with_ai(request: AIRequest):
    return AIResponse(response=f"AI response to: {request.prompt}")


# ======================== AI 专家管理 API ========================


@router.get("/experts", response_model=AIExpertListResponse)
async def list_experts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词(名称或编码)"),
    status: Optional[str] = Query(None, description="状态筛选(active/inactive/draft)"),
    category: Optional[str] = Query(None, description="分类筛选"),
    db: Session = Depends(get_db),
):
    """获取AI专家列表（支持分页、搜索、筛选）"""
    query = db.query(AIExpertORM)

    if keyword:
        query = query.filter(
            or_(
                AIExpertORM.name.ilike(f"%{keyword}%"),
                AIExpertORM.code.ilike(f"%{keyword}%"),
            )
        )

    if status and status in ["active", "inactive", "draft"]:
        query = query.filter(AIExpertORM.status == status)

    if category:
        query = query.filter(AIExpertORM.category == category)

    total = query.count()
    items = (
        query.order_by(AIExpertORM.sort_order)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return AIExpertListResponse(
        total=total,
        items=items,
        page=page,
        page_size=page_size
    )


@router.get("/experts/categories")
async def list_expert_categories(db: Session = Depends(get_db)):
    """获取专家分类列表"""

    rows = (
        db.query(AIExpertORM.category)
        .filter(AIExpertORM.category.isnot(None))
        .distinct()
        .all()
    )
    categories = [row[0] for row in rows if row[0]]
    return {"items": sorted(categories)}


@router.get("/experts/{expert_id}", response_model=AIExpertResponse)
async def get_expert(expert_id: int, db: Session = Depends(get_db)):
    """获取单个AI专家详情"""
    expert = db.query(AIExpertORM).filter(AIExpertORM.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail=f"AI专家 ID {expert_id} 不存在")
    return expert


@router.post("/experts", response_model=AIExpertResponse)
async def create_expert(expert: AIExpertCreate, db: Session = Depends(get_db)):
    """创建新的AI专家"""
    exists = db.query(AIExpertORM).filter(AIExpertORM.code == expert.code).first()
    if exists:
        raise HTTPException(status_code=400, detail=f"专家编码 '{expert.code}' 已存在")

    now = datetime.now()
    new_expert = AIExpertORM(
        **expert.model_dump(),
        usage_count=0,
        created_time=now,
        updated_by=None,
        updated_time=None,
    )
    db.add(new_expert)
    db.commit()
    db.refresh(new_expert)

    knowledge_base = KnowledgeBaseORM(
        expert_id=new_expert.id,
        name=f"{new_expert.name}知识库",
        description="",
    )
    skill_base = SkillBaseORM(
        expert_id=new_expert.id,
        name=f"{new_expert.name}技能库",
        description="",
    )
    db.add(knowledge_base)
    db.add(skill_base)
    db.commit()

    return new_expert


@router.put("/experts/{expert_id}", response_model=AIExpertResponse)
async def update_expert(expert_id: int, expert: AIExpertUpdate, db: Session = Depends(get_db)):
    """更新AI专家信息"""
    db_expert = db.query(AIExpertORM).filter(AIExpertORM.id == expert_id).first()
    if not db_expert:
        raise HTTPException(status_code=404, detail=f"AI专家 ID {expert_id} 不存在")

    if expert.code and expert.code != db_expert.code:
        exists = (
            db.query(AIExpertORM)
            .filter(AIExpertORM.code == expert.code, AIExpertORM.id != expert_id)
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail=f"专家编码 '{expert.code}' 已存在")

    update_data = expert.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_expert, key, value)
    db_expert.updated_time = datetime.now()
    db.commit()
    db.refresh(db_expert)
    return db_expert


@router.delete("/experts/{expert_id}")
async def delete_expert(expert_id: int, db: Session = Depends(get_db)):
    """删除AI专家"""
    expert = db.query(AIExpertORM).filter(AIExpertORM.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail=f"AI专家 ID {expert_id} 不存在")

    db.delete(expert)
    db.commit()
    return {"message": "删除成功", "expert_id": expert_id}


@router.patch("/experts/{expert_id}/status")
async def update_expert_status(
    expert_id: int,
    status: str = Query(..., pattern="^(active|inactive|draft)$"),
    db: Session = Depends(get_db),
):
    """更新AI专家状态"""
    expert = db.query(AIExpertORM).filter(AIExpertORM.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail=f"AI专家 ID {expert_id} 不存在")

    expert.status = status
    expert.updated_time = datetime.now()
    db.commit()
    return {"message": "状态更新成功", "id": expert_id, "status": status}


# ======================== 子智能体管理 ========================


@router.get("/experts/{expert_id}/sub-agents", response_model=SubAgentListResponse)
async def list_sub_agents(expert_id: int, db: Session = Depends(get_db)):
    """获取子智能体列表"""

    items = db.query(SubAgentORM).filter(SubAgentORM.expert_id == expert_id).order_by(SubAgentORM.id.desc()).all()
    return SubAgentListResponse(total=len(items), items=items)


@router.post("/experts/{expert_id}/sub-agents", response_model=SubAgentResponse)
async def create_sub_agent(expert_id: int, payload: SubAgentCreate, db: Session = Depends(get_db)):
    """创建子智能体"""

    expert = db.query(AIExpertORM).filter(AIExpertORM.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="专家不存在")

    sub_agent = SubAgentORM(
        expert_id=expert_id,
        name=payload.name,
        description=payload.description,
        prompt=payload.prompt,
        status=payload.status,
    )
    db.add(sub_agent)
    db.commit()
    db.refresh(sub_agent)
    return sub_agent


@router.get("/experts/{expert_id}/sub-agents/{sub_agent_id}", response_model=SubAgentResponse)
async def get_sub_agent(expert_id: int, sub_agent_id: int, db: Session = Depends(get_db)):
    """获取子智能体详情"""

    sub_agent = (
        db.query(SubAgentORM)
        .filter(SubAgentORM.id == sub_agent_id, SubAgentORM.expert_id == expert_id)
        .first()
    )
    if not sub_agent:
        raise HTTPException(status_code=404, detail="子智能体不存在")
    return sub_agent


@router.put("/experts/{expert_id}/sub-agents/{sub_agent_id}", response_model=SubAgentResponse)
async def update_sub_agent(
    expert_id: int,
    sub_agent_id: int,
    payload: SubAgentUpdate,
    db: Session = Depends(get_db),
):
    """更新子智能体"""

    sub_agent = (
        db.query(SubAgentORM)
        .filter(SubAgentORM.id == sub_agent_id, SubAgentORM.expert_id == expert_id)
        .first()
    )
    if not sub_agent:
        raise HTTPException(status_code=404, detail="子智能体不存在")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sub_agent, key, value)
    db.commit()
    db.refresh(sub_agent)
    return sub_agent


@router.delete("/experts/{expert_id}/sub-agents/{sub_agent_id}")
async def delete_sub_agent(expert_id: int, sub_agent_id: int, db: Session = Depends(get_db)):
    """删除子智能体"""

    sub_agent = (
        db.query(SubAgentORM)
        .filter(SubAgentORM.id == sub_agent_id, SubAgentORM.expert_id == expert_id)
        .first()
    )
    if not sub_agent:
        raise HTTPException(status_code=404, detail="子智能体不存在")

    db.delete(sub_agent)
    db.commit()
    return {"message": "删除成功", "id": sub_agent_id}

