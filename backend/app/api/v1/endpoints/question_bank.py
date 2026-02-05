from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.models import AIExpertORM, QuestionBaseORM, QuestionItemORM
from app.models.question_bank import (
    QuestionBaseUpdate,
    QuestionBaseResponse,
    QuestionItemCreate,
    QuestionItemUpdate,
    QuestionItemResponse,
)

router = APIRouter()


def _success(data):
    """统一成功响应"""

    return {"success": True, "data": data}


def _error(message: str, status_code: int = 400):
    """统一错误响应"""

    return JSONResponse(status_code=status_code, content={"success": False, "error": message})


async def _get_or_create_question_base(db: AsyncSession, expert_id: int) -> QuestionBaseORM:
    """获取或创建专家问题库"""

    base_result = await db.execute(
        select(QuestionBaseORM).where(QuestionBaseORM.expert_id == expert_id)
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

    base = QuestionBaseORM(
        expert_id=expert_id,
        name=f"{expert.name}问题库",
        description="",
    )
    db.add(base)
    await db.commit()
    await db.refresh(base)
    return base


@router.get("/experts/{expert_id}/question-base")
async def get_question_base(expert_id: int, db: AsyncSession = Depends(get_db)):
    """获取专家问题库"""

    try:
        base = await _get_or_create_question_base(db, expert_id)
        return _success(QuestionBaseResponse.model_validate(base).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.put("/experts/{expert_id}/question-base")
async def update_question_base(
    expert_id: int,
    payload: QuestionBaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新专家问题库"""

    try:
        base = await _get_or_create_question_base(db, expert_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(base, key, value)
        await db.commit()
        await db.refresh(base)
        return _success(QuestionBaseResponse.model_validate(base).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.get("/experts/{expert_id}/questions")
async def list_question_items(
    expert_id: int,
    category: str | None = Query(None, description="分类过滤"),
    enabled: bool | None = Query(None, description="启用状态过滤"),
    db: AsyncSession = Depends(get_db),
):
    """获取问题库条目列表"""

    try:
        base = await _get_or_create_question_base(db, expert_id)
        query = (
            select(QuestionItemORM)
            .where(QuestionItemORM.question_base_id == base.id)
            .order_by(QuestionItemORM.id.desc())
        )

        if category:
            query = query.where(QuestionItemORM.category == category)
        if enabled is not None:
            query = query.where(QuestionItemORM.enabled == enabled)

        result = await db.execute(query)
        items = result.scalars().all()
        data = [QuestionItemResponse.model_validate(item).model_dump() for item in items]
        return _success(data)
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.post("/experts/{expert_id}/questions")
async def create_question_item(
    expert_id: int,
    payload: QuestionItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建问题库条目"""

    try:
        base = await _get_or_create_question_base(db, expert_id)
        item = QuestionItemORM(
            question_base_id=base.id,
            question=payload.question,
            answer=payload.answer,
            category=payload.category,
            tags=payload.tags,
            difficulty=payload.difficulty,
            enabled=payload.enabled,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return _success(QuestionItemResponse.model_validate(item).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.get("/experts/{expert_id}/questions/{item_id}")
async def get_question_item(
    expert_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取问题库条目详情"""

    try:
        base = await _get_or_create_question_base(db, expert_id)
        result = await db.execute(
            select(QuestionItemORM).where(
                QuestionItemORM.id == item_id,
                QuestionItemORM.question_base_id == base.id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("问题条目不存在", status_code=404)
        return _success(QuestionItemResponse.model_validate(item).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.put("/experts/{expert_id}/questions/{item_id}")
async def update_question_item(
    expert_id: int,
    item_id: int,
    payload: QuestionItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新问题库条目"""

    try:
        base = await _get_or_create_question_base(db, expert_id)
        result = await db.execute(
            select(QuestionItemORM).where(
                QuestionItemORM.id == item_id,
                QuestionItemORM.question_base_id == base.id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("问题条目不存在", status_code=404)

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        await db.commit()
        await db.refresh(item)
        return _success(QuestionItemResponse.model_validate(item).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.delete("/experts/{expert_id}/questions/{item_id}")
async def delete_question_item(
    expert_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除问题库条目"""

    try:
        base = await _get_or_create_question_base(db, expert_id)
        result = await db.execute(
            select(QuestionItemORM).where(
                QuestionItemORM.id == item_id,
                QuestionItemORM.question_base_id == base.id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("问题条目不存在", status_code=404)

        await db.delete(item)
        await db.commit()
        return _success({"id": item_id})
    except ValueError as e:
        return _error(str(e), status_code=404)
