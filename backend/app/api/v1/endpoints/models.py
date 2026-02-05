from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.db.models import ModelConfigORM
from app.services.permission_service import filter_query_by_user_permissions, has_user_permission
from app.models.model_config import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigResponse,
    ModelConfigListResponse,
)

router = APIRouter()


@router.get("/", response_model=ModelConfigListResponse)
async def list_model_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    enabled: Optional[bool] = Query(None),
    user_id: Optional[int] = Query(None, description="按用户权限过滤"),
    db: AsyncSession = Depends(get_db),
):
    """获取模型配置列表"""
    query = select(ModelConfigORM)

    if keyword:
        query = query.where(
            or_(
                ModelConfigORM.name.ilike(f"%{keyword}%"),
                ModelConfigORM.model_name.ilike(f"%{keyword}%"),
            )
        )

    if provider:
        query = query.where(ModelConfigORM.provider == provider)

    if enabled is not None:
        query = query.where(ModelConfigORM.enabled == enabled)

    try:
        query = await filter_query_by_user_permissions(
            db, query, user_id, "model", ModelConfigORM.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    result = await db.execute(
        query.order_by(ModelConfigORM.created_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = result.scalars().all()

    return ModelConfigListResponse(
        total=total or 0,
        items=items,
        page=page,
        page_size=page_size,
    )


@router.get("/{config_id}", response_model=ModelConfigResponse)
async def get_model_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """获取模型配置详情"""
    result = await db.execute(
        select(ModelConfigORM).where(ModelConfigORM.id == config_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    return config


@router.get("/{config_id}/by-user", response_model=ModelConfigResponse)
async def get_model_config_for_user(
    config_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取用户有权限的模型配置详情"""
    result = await db.execute(
        select(ModelConfigORM).where(ModelConfigORM.id == config_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    try:
        allowed = await has_user_permission(db, user_id, "model", config_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if not allowed:
        raise HTTPException(status_code=403, detail="无权限访问该模型配置")
    return config


@router.post("/", response_model=ModelConfigResponse)
async def create_model_config(
    config: ModelConfigCreate, db: AsyncSession = Depends(get_db)
):
    """创建模型配置"""
    new_config = ModelConfigORM(**config.model_dump())
    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)
    return new_config


@router.put("/{config_id}", response_model=ModelConfigResponse)
async def update_model_config(
    config_id: int, config: ModelConfigUpdate, db: AsyncSession = Depends(get_db)
):
    """更新模型配置"""
    result = await db.execute(
        select(ModelConfigORM).where(ModelConfigORM.id == config_id)
    )
    db_config = result.scalar_one_or_none()
    if not db_config:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    update_data = config.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_config, key, value)

    await db.commit()
    await db.refresh(db_config)
    return db_config


@router.delete("/{config_id}")
async def delete_model_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """删除模型配置"""
    result = await db.execute(
        select(ModelConfigORM).where(ModelConfigORM.id == config_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    await db.delete(config)
    await db.commit()
    return {"message": "删除成功", "config_id": config_id}
