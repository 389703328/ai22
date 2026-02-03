from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.models import KnowledgeGraphORM, AIExpertORM
from app.models.knowledge_graph import (
    KnowledgeGraphCreate,
    KnowledgeGraphUpdate,
    KnowledgeGraphResponse,
    KnowledgeGraphListResponse,
)

router = APIRouter()


@router.get("/experts/{expert_id}/knowledge-graphs", response_model=KnowledgeGraphListResponse)
async def list_knowledge_graphs(expert_id: int, db: AsyncSession = Depends(get_db)):
    """获取专家的知识图谱列表"""
    result = await db.execute(
        select(KnowledgeGraphORM)
        .where(KnowledgeGraphORM.expert_id == expert_id)
        .order_by(KnowledgeGraphORM.created_time.desc())
    )
    items = result.scalars().all()
    return KnowledgeGraphListResponse(total=len(items), items=items)


@router.post("/experts/{expert_id}/knowledge-graphs", response_model=KnowledgeGraphResponse)
async def create_knowledge_graph(
    expert_id: int, graph: KnowledgeGraphCreate, db: AsyncSession = Depends(get_db)
):
    """创建知识图谱"""
    # 验证专家存在
    expert_result = await db.execute(
        select(AIExpertORM).where(AIExpertORM.id == expert_id)
    )
    if not expert_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="专家不存在")

    new_graph = KnowledgeGraphORM(expert_id=expert_id, **graph.model_dump(exclude={"expert_id"}))
    db.add(new_graph)
    await db.commit()
    await db.refresh(new_graph)
    return new_graph


@router.get("/experts/{expert_id}/knowledge-graphs/{graph_id}", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(
    expert_id: int, graph_id: int, db: AsyncSession = Depends(get_db)
):
    """获取知识图谱详情"""
    result = await db.execute(
        select(KnowledgeGraphORM).where(
            KnowledgeGraphORM.id == graph_id,
            KnowledgeGraphORM.expert_id == expert_id,
        )
    )
    graph = result.scalar_one_or_none()
    if not graph:
        raise HTTPException(status_code=404, detail="知识图谱不存在")
    return graph


@router.put("/experts/{expert_id}/knowledge-graphs/{graph_id}", response_model=KnowledgeGraphResponse)
async def update_knowledge_graph(
    expert_id: int,
    graph_id: int,
    graph: KnowledgeGraphUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新知识图谱"""
    result = await db.execute(
        select(KnowledgeGraphORM).where(
            KnowledgeGraphORM.id == graph_id,
            KnowledgeGraphORM.expert_id == expert_id,
        )
    )
    db_graph = result.scalar_one_or_none()
    if not db_graph:
        raise HTTPException(status_code=404, detail="知识图谱不存在")

    update_data = graph.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_graph, key, value)

    await db.commit()
    await db.refresh(db_graph)
    return db_graph


@router.delete("/experts/{expert_id}/knowledge-graphs/{graph_id}")
async def delete_knowledge_graph(
    expert_id: int, graph_id: int, db: AsyncSession = Depends(get_db)
):
    """删除知识图谱"""
    result = await db.execute(
        select(KnowledgeGraphORM).where(
            KnowledgeGraphORM.id == graph_id,
            KnowledgeGraphORM.expert_id == expert_id,
        )
    )
    graph = result.scalar_one_or_none()
    if not graph:
        raise HTTPException(status_code=404, detail="知识图谱不存在")

    await db.delete(graph)
    await db.commit()
    return {"message": "删除成功", "graph_id": graph_id}
