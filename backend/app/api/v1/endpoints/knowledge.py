from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import AIExpertORM, KnowledgeBaseORM, KnowledgeItemORM
from app.models.knowledge import (
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeItemCreate,
    KnowledgeItemUpdate,
    KnowledgeItemResponse,
)

router = APIRouter()


def _success(data):
    """统一成功响应"""

    return {"success": True, "data": data}


def _error(message: str, status_code: int = 400):
    """统一错误响应"""

    return JSONResponse(status_code=status_code, content={"success": False, "error": message})


def _knowledge_item_to_response(item: KnowledgeItemORM) -> dict:
    """知识条目ORM -> 响应数据"""

    return KnowledgeItemResponse(
        id=item.id,
        knowledge_base_id=item.knowledge_base_id,
        title=item.title,
        content=item.content,
        metadata=item.metadata_json,
        enabled=item.enabled,
        created_time=item.created_time,
        updated_time=item.updated_time,
    ).model_dump()


def _get_or_create_knowledge_base(db: Session, expert_id: int) -> KnowledgeBaseORM:
    """获取或创建专家知识库"""

    base = db.query(KnowledgeBaseORM).filter(KnowledgeBaseORM.expert_id == expert_id).first()
    if base:
        return base

    expert = db.query(AIExpertORM).filter(AIExpertORM.id == expert_id).first()
    if not expert:
        raise ValueError("专家不存在")

    base = KnowledgeBaseORM(
        expert_id=expert_id,
        name=f"{expert.name}知识库",
        description="",
    )
    db.add(base)
    db.commit()
    db.refresh(base)
    return base


@router.get("/experts/{expert_id}/knowledge-base")
def get_knowledge_base(expert_id: int, db: Session = Depends(get_db)):
    """获取专家知识库"""

    try:
        base = _get_or_create_knowledge_base(db, expert_id)
        return _success(KnowledgeBaseResponse.model_validate(base).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.put("/experts/{expert_id}/knowledge-base")
def update_knowledge_base(
    expert_id: int,
    payload: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
):
    """更新专家知识库"""

    try:
        base = _get_or_create_knowledge_base(db, expert_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(base, key, value)
        db.commit()
        db.refresh(base)
        return _success(KnowledgeBaseResponse.model_validate(base).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.get("/experts/{expert_id}/knowledge/items")
def list_knowledge_items(
    expert_id: int,
    db: Session = Depends(get_db),
):
    """获取知识库条目列表"""

    try:
        base = _get_or_create_knowledge_base(db, expert_id)
        items = (
            db.query(KnowledgeItemORM)
            .filter(KnowledgeItemORM.knowledge_base_id == base.id)
            .order_by(KnowledgeItemORM.id.desc())
            .all()
        )
        data = [_knowledge_item_to_response(item) for item in items]
        return _success(data)
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.post("/experts/{expert_id}/knowledge/items")
def create_knowledge_item(
    expert_id: int,
    payload: KnowledgeItemCreate,
    db: Session = Depends(get_db),
):
    """创建知识库条目"""

    try:
        base = _get_or_create_knowledge_base(db, expert_id)
        item = KnowledgeItemORM(
            knowledge_base_id=base.id,
            title=payload.title,
            content=payload.content,
            metadata_json=payload.metadata,
            enabled=payload.enabled,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return _success(_knowledge_item_to_response(item))
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.get("/experts/{expert_id}/knowledge/items/{item_id}")
def get_knowledge_item(
    expert_id: int,
    item_id: int,
    db: Session = Depends(get_db),
):
    """获取知识库条目详情"""

    try:
        base = _get_or_create_knowledge_base(db, expert_id)
        item = (
            db.query(KnowledgeItemORM)
            .filter(
                KnowledgeItemORM.id == item_id,
                KnowledgeItemORM.knowledge_base_id == base.id,
            )
            .first()
        )
        if not item:
            return _error("知识条目不存在", status_code=404)
        return _success(_knowledge_item_to_response(item))
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.put("/experts/{expert_id}/knowledge/items/{item_id}")
def update_knowledge_item(
    expert_id: int,
    item_id: int,
    payload: KnowledgeItemUpdate,
    db: Session = Depends(get_db),
):
    """更新知识库条目"""

    try:
        base = _get_or_create_knowledge_base(db, expert_id)
        item = (
            db.query(KnowledgeItemORM)
            .filter(
                KnowledgeItemORM.id == item_id,
                KnowledgeItemORM.knowledge_base_id == base.id,
            )
            .first()
        )
        if not item:
            return _error("知识条目不存在", status_code=404)

        update_data = payload.model_dump(exclude_unset=True)
        if "metadata" in update_data:
            item.metadata_json = update_data.pop("metadata")
        for key, value in update_data.items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return _success(_knowledge_item_to_response(item))
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.delete("/experts/{expert_id}/knowledge/items/{item_id}")
def delete_knowledge_item(
    expert_id: int,
    item_id: int,
    db: Session = Depends(get_db),
):
    """删除知识库条目"""

    try:
        base = _get_or_create_knowledge_base(db, expert_id)
        item = (
            db.query(KnowledgeItemORM)
            .filter(
                KnowledgeItemORM.id == item_id,
                KnowledgeItemORM.knowledge_base_id == base.id,
            )
            .first()
        )
        if not item:
            return _error("知识条目不存在", status_code=404)

        db.delete(item)
        db.commit()
        return _success({"id": item_id})
    except ValueError as e:
        return _error(str(e), status_code=404)
