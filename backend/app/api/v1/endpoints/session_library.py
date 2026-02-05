from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.models import SubAgentORM, SubAgentSessionORM
from app.models.session_library import (
    SubAgentSessionCreate,
    SubAgentSessionUpdate,
    SubAgentSessionResponse,
    SubAgentSessionListResponse,
)

router = APIRouter()


def _success(data):
    """统一成功响应"""

    return {"success": True, "data": data}


def _error(message: str, status_code: int = 400):
    """统一错误响应"""

    return JSONResponse(status_code=status_code, content={"success": False, "error": message})


async def _get_sub_agent(db: AsyncSession, sub_agent_id: int) -> SubAgentORM:
    """获取子智能体"""

    result = await db.execute(
        select(SubAgentORM).where(SubAgentORM.id == sub_agent_id)
    )
    sub_agent = result.scalar_one_or_none()
    if not sub_agent:
        raise ValueError("子智能体不存在")
    return sub_agent


@router.get("/sub-agents/{sub_agent_id}/sessions")
async def list_sub_agent_sessions(
    sub_agent_id: int,
    user_id: int | None = Query(None, description="按用户过滤"),
    feedback_type: str | None = Query(None, description="反馈类型过滤"),
    db: AsyncSession = Depends(get_db),
):
    """获取子智能体会话列表"""

    try:
        await _get_sub_agent(db, sub_agent_id)
        query = (
            select(SubAgentSessionORM)
            .where(SubAgentSessionORM.sub_agent_id == sub_agent_id)
            .order_by(SubAgentSessionORM.id.desc())
        )
        if user_id is not None:
            query = query.where(SubAgentSessionORM.user_id == user_id)
        if feedback_type:
            query = query.where(SubAgentSessionORM.feedback_type == feedback_type)

        result = await db.execute(query)
        items = result.scalars().all()
        data = [SubAgentSessionResponse.model_validate(item).model_dump() for item in items]
        return _success(SubAgentSessionListResponse(total=len(items), items=data).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.post("/sub-agents/{sub_agent_id}/sessions")
async def create_sub_agent_session(
    sub_agent_id: int,
    payload: SubAgentSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建子智能体会话"""

    try:
        await _get_sub_agent(db, sub_agent_id)
        item = SubAgentSessionORM(
            sub_agent_id=sub_agent_id,
            user_id=payload.user_id,
            session_id=payload.session_id,
            title=payload.title,
            content=payload.content,
            feedback_type=payload.feedback_type,
            comment=payload.comment,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return _success(SubAgentSessionResponse.model_validate(item).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.get("/sub-agents/{sub_agent_id}/sessions/{session_id}")
async def get_sub_agent_session(
    sub_agent_id: int,
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取子智能体会话详情"""

    try:
        await _get_sub_agent(db, sub_agent_id)
        result = await db.execute(
            select(SubAgentSessionORM).where(
                SubAgentSessionORM.id == session_id,
                SubAgentSessionORM.sub_agent_id == sub_agent_id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("会话不存在", status_code=404)
        return _success(SubAgentSessionResponse.model_validate(item).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.put("/sub-agents/{sub_agent_id}/sessions/{session_id}")
async def update_sub_agent_session(
    sub_agent_id: int,
    session_id: int,
    payload: SubAgentSessionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新子智能体会话"""

    try:
        await _get_sub_agent(db, sub_agent_id)
        result = await db.execute(
            select(SubAgentSessionORM).where(
                SubAgentSessionORM.id == session_id,
                SubAgentSessionORM.sub_agent_id == sub_agent_id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("会话不存在", status_code=404)

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        await db.commit()
        await db.refresh(item)
        return _success(SubAgentSessionResponse.model_validate(item).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.delete("/sub-agents/{sub_agent_id}/sessions/{session_id}")
async def delete_sub_agent_session(
    sub_agent_id: int,
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除子智能体会话"""

    try:
        await _get_sub_agent(db, sub_agent_id)
        result = await db.execute(
            select(SubAgentSessionORM).where(
                SubAgentSessionORM.id == session_id,
                SubAgentSessionORM.sub_agent_id == sub_agent_id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("会话不存在", status_code=404)

        await db.delete(item)
        await db.commit()
        return _success({"id": session_id})
    except ValueError as e:
        return _error(str(e), status_code=404)
