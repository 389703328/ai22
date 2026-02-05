from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.models import AIExpertORM, KnowledgeBaseORM, KnowledgeItemORM
from app.services.permission_service import filter_query_by_user_permissions, has_user_permission
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
        name=item.name or item.title,
        text=item.text or item.content,
        title=item.title,
        content=item.content,
        file_path=item.file_path,
        file_name=item.file_name,
        sub_agent_id=item.sub_agent_id,
        metadata=item.metadata_json,
        indexing_technique=item.indexing_technique,
        doc_form=item.doc_form,
        doc_language=item.doc_language,
        process_rule=item.process_rule,
        retrieval_model=item.retrieval_model,
        embedding_model=item.embedding_model,
        embedding_model_provider=item.embedding_model_provider,
        enabled=item.enabled,
        created_time=item.created_time,
        updated_time=item.updated_time,
    ).model_dump()


async def _get_or_create_knowledge_base(db: AsyncSession, expert_id: int) -> KnowledgeBaseORM:
    """获取或创建专家知识库"""

    base_result = await db.execute(
        select(KnowledgeBaseORM).where(KnowledgeBaseORM.expert_id == expert_id)
    )
    base = base_result.scalar_one_or_none()
    if base:
        return base

    expert_result = await db.execute(
        select(AIExpertORM).where(AIExpertORM.id == expert_id)
    )
    expert = expert_result.scalar_one_or_none()
    if not expert:
        raise ValueError("专家不存在")

    base = KnowledgeBaseORM(
        expert_id=expert_id,
        name=f"{expert.name}知识库",
        description="",
    )
    db.add(base)
    await db.commit()
    await db.refresh(base)
    return base


@router.get("/experts/{expert_id}/knowledge-base")
async def get_knowledge_base(expert_id: int, db: AsyncSession = Depends(get_db)):
    """获取专家知识库"""

    try:
        base = await _get_or_create_knowledge_base(db, expert_id)
        return _success(KnowledgeBaseResponse.model_validate(base).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.put("/experts/{expert_id}/knowledge-base")
async def update_knowledge_base(
    expert_id: int,
    payload: KnowledgeBaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新专家知识库"""

    try:
        base = await _get_or_create_knowledge_base(db, expert_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(base, key, value)
        await db.commit()
        await db.refresh(base)
        return _success(KnowledgeBaseResponse.model_validate(base).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.get("/experts/{expert_id}/knowledge/items")
async def list_knowledge_items(
    expert_id: int,
    user_id: int | None = Query(None, description="按用户权限过滤"),
    sub_agent_id: int | None = Query(None, description="按子智能体过滤"),
    db: AsyncSession = Depends(get_db),
):
    """获取知识库条目列表"""

    try:
        base = await _get_or_create_knowledge_base(db, expert_id)
        query = (
            select(KnowledgeItemORM)
            .where(KnowledgeItemORM.knowledge_base_id == base.id)
            .order_by(KnowledgeItemORM.id.desc())
        )

        if sub_agent_id is not None:
            query = query.where(KnowledgeItemORM.sub_agent_id == sub_agent_id)

        if user_id is not None:
            try:
                has_expert_access = await has_user_permission(db, user_id, "expert", expert_id)
            except ValueError as e:
                return _error(str(e), status_code=404)

            if not has_expert_access:
                try:
                    query = await filter_query_by_user_permissions(
                        db, query, user_id, "knowledge", KnowledgeItemORM.id
                    )
                except ValueError as e:
                    return _error(str(e), status_code=404)

        result = await db.execute(query)
        items = result.scalars().all()
        data = [_knowledge_item_to_response(item) for item in items]
        return _success(data)
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.post("/experts/{expert_id}/knowledge/items")
async def create_knowledge_item(
    expert_id: int,
    payload: KnowledgeItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建知识库条目"""

    try:
        base = await _get_or_create_knowledge_base(db, expert_id)
        title_value = payload.name or payload.title
        content_value = payload.text or payload.content or ""
        item = KnowledgeItemORM(
            knowledge_base_id=base.id,
            title=title_value,
            content=content_value,
            name=payload.name,
            text=payload.text,
            file_path=payload.file_path,
            file_name=payload.file_name,
            sub_agent_id=payload.sub_agent_id,
            metadata_json=payload.metadata,
            indexing_technique=payload.indexing_technique,
            doc_form=payload.doc_form,
            doc_language=payload.doc_language,
            process_rule=payload.process_rule,
            retrieval_model=payload.retrieval_model,
            embedding_model=payload.embedding_model,
            embedding_model_provider=payload.embedding_model_provider,
            enabled=payload.enabled,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return _success(_knowledge_item_to_response(item))
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.get("/experts/{expert_id}/knowledge/items/{item_id}")
async def get_knowledge_item(
    expert_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取知识库条目详情"""

    try:
        base = await _get_or_create_knowledge_base(db, expert_id)
        result = await db.execute(
            select(KnowledgeItemORM).where(
                KnowledgeItemORM.id == item_id,
                KnowledgeItemORM.knowledge_base_id == base.id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("知识条目不存在", status_code=404)
        return _success(_knowledge_item_to_response(item))
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.get("/experts/{expert_id}/knowledge/items/{item_id}/by-user")
async def get_knowledge_item_for_user(
    expert_id: int,
    item_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取用户有权限的知识条目详情"""
    try:
        base = await _get_or_create_knowledge_base(db, expert_id)
        result = await db.execute(
            select(KnowledgeItemORM).where(
                KnowledgeItemORM.id == item_id,
                KnowledgeItemORM.knowledge_base_id == base.id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("知识条目不存在", status_code=404)

        has_expert_access = await has_user_permission(db, user_id, "expert", expert_id)
        if not has_expert_access:
            has_item_access = await has_user_permission(db, user_id, "knowledge", item_id)
            if not has_item_access:
                return _error("无权限访问该知识条目", status_code=403)

        return _success(_knowledge_item_to_response(item))
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.put("/experts/{expert_id}/knowledge/items/{item_id}")
async def update_knowledge_item(
    expert_id: int,
    item_id: int,
    payload: KnowledgeItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新知识库条目"""

    try:
        base = await _get_or_create_knowledge_base(db, expert_id)
        result = await db.execute(
            select(KnowledgeItemORM).where(
                KnowledgeItemORM.id == item_id,
                KnowledgeItemORM.knowledge_base_id == base.id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("知识条目不存在", status_code=404)

        update_data = payload.model_dump(exclude_unset=True)
        if "metadata" in update_data:
            item.metadata_json = update_data.pop("metadata")
        if "process_rule" in update_data:
            item.process_rule = update_data.pop("process_rule")
        if "retrieval_model" in update_data:
            item.retrieval_model = update_data.pop("retrieval_model")

        if "name" in update_data:
            item.title = update_data["name"]
        if "text" in update_data:
            item.content = update_data["text"] or item.content
        if "title" in update_data:
            item.title = update_data["title"]
        if "content" in update_data:
            item.content = update_data["content"] or item.content

        for key, value in update_data.items():
            setattr(item, key, value)
        await db.commit()
        await db.refresh(item)
        return _success(_knowledge_item_to_response(item))
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.delete("/experts/{expert_id}/knowledge/items/{item_id}")
async def delete_knowledge_item(
    expert_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除知识库条目"""

    try:
        base = await _get_or_create_knowledge_base(db, expert_id)
        result = await db.execute(
            select(KnowledgeItemORM).where(
                KnowledgeItemORM.id == item_id,
                KnowledgeItemORM.knowledge_base_id == base.id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("知识条目不存在", status_code=404)

        await db.delete(item)
        await db.commit()
        return _success({"id": item_id})
    except ValueError as e:
        return _error(str(e), status_code=404)
