from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.models import AIExpertORM, SkillBaseORM, SkillItemORM
from app.models.skill import (
    SkillBaseUpdate,
    SkillBaseResponse,
    SkillItemCreate,
    SkillItemUpdate,
    SkillItemResponse,
)

router = APIRouter()


def _success(data):
    """统一成功响应"""

    return {"success": True, "data": data}


def _error(message: str, status_code: int = 400):
    """统一错误响应"""

    return JSONResponse(status_code=status_code, content={"success": False, "error": message})


async def _get_or_create_skill_base(db: AsyncSession, expert_id: int) -> SkillBaseORM:
    """获取或创建专家技能库"""

    base_result = await db.execute(
        select(SkillBaseORM).where(SkillBaseORM.expert_id == expert_id)
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

    base = SkillBaseORM(
        expert_id=expert_id,
        name=f"{expert.name}技能库",
        description="",
    )
    db.add(base)
    await db.commit()
    await db.refresh(base)
    return base


@router.get("/experts/{expert_id}/skill-base")
async def get_skill_base(expert_id: int, db: AsyncSession = Depends(get_db)):
    """获取专家技能库"""

    try:
        base = await _get_or_create_skill_base(db, expert_id)
        return _success(SkillBaseResponse.model_validate(base).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.put("/experts/{expert_id}/skill-base")
async def update_skill_base(
    expert_id: int,
    payload: SkillBaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新专家技能库"""

    try:
        base = await _get_or_create_skill_base(db, expert_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(base, key, value)
        await db.commit()
        await db.refresh(base)
        return _success(SkillBaseResponse.model_validate(base).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.get("/experts/{expert_id}/skills")
async def list_skill_items(
    expert_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取技能库条目列表"""

    try:
        base = await _get_or_create_skill_base(db, expert_id)
        result = await db.execute(
            select(SkillItemORM)
            .where(SkillItemORM.skill_base_id == base.id)
            .order_by(SkillItemORM.id.desc())
        )
        items = result.scalars().all()
        data = [SkillItemResponse.model_validate(item).model_dump() for item in items]
        return _success(data)
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.post("/experts/{expert_id}/skills")
async def create_skill_item(
    expert_id: int,
    payload: SkillItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建技能库条目"""

    try:
        base = await _get_or_create_skill_base(db, expert_id)
        item = SkillItemORM(
            skill_base_id=base.id,
            name=payload.name,
            description=payload.description,
            content=payload.content,
            file_path=payload.file_path,
            file_name=payload.file_name,
            category=payload.category,
            tags=payload.tags,
            enabled=payload.enabled,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return _success(SkillItemResponse.model_validate(item).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.get("/experts/{expert_id}/skills/{item_id}")
async def get_skill_item(
    expert_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取技能库条目详情"""

    try:
        base = await _get_or_create_skill_base(db, expert_id)
        result = await db.execute(
            select(SkillItemORM).where(
                SkillItemORM.id == item_id,
                SkillItemORM.skill_base_id == base.id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("技能条目不存在", status_code=404)
        return _success(SkillItemResponse.model_validate(item).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.put("/experts/{expert_id}/skills/{item_id}")
async def update_skill_item(
    expert_id: int,
    item_id: int,
    payload: SkillItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新技能库条目"""

    try:
        base = await _get_or_create_skill_base(db, expert_id)
        result = await db.execute(
            select(SkillItemORM).where(
                SkillItemORM.id == item_id,
                SkillItemORM.skill_base_id == base.id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("技能条目不存在", status_code=404)

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        await db.commit()
        await db.refresh(item)
        return _success(SkillItemResponse.model_validate(item).model_dump())
    except ValueError as e:
        return _error(str(e), status_code=404)


@router.delete("/experts/{expert_id}/skills/{item_id}")
async def delete_skill_item(
    expert_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除技能库条目"""

    try:
        base = await _get_or_create_skill_base(db, expert_id)
        result = await db.execute(
            select(SkillItemORM).where(
                SkillItemORM.id == item_id,
                SkillItemORM.skill_base_id == base.id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return _error("技能条目不存在", status_code=404)

        await db.delete(item)
        await db.commit()
        return _success({"id": item_id})
    except ValueError as e:
        return _error(str(e), status_code=404)
