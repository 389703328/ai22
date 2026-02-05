from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.db.models import MCPToolORM
from app.services.permission_service import filter_query_by_user_permissions, has_user_permission
from app.models.mcp import (
    MCPToolCreate,
    MCPToolUpdate,
    MCPToolResponse,
    MCPToolListResponse,
)

router = APIRouter()


@router.get("/", response_model=MCPToolListResponse)
async def list_mcp_tools(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    tool_type: Optional[str] = Query(None),
    enabled: Optional[bool] = Query(None),
    user_id: Optional[int] = Query(None, description="按用户权限过滤"),
    db: AsyncSession = Depends(get_db),
):
    """获取MCP工具列表"""
    query = select(MCPToolORM)

    if keyword:
        query = query.where(
            or_(
                MCPToolORM.name.ilike(f"%{keyword}%"),
                MCPToolORM.description.ilike(f"%{keyword}%"),
            )
        )

    if tool_type:
        query = query.where(MCPToolORM.tool_type == tool_type)

    if enabled is not None:
        query = query.where(MCPToolORM.enabled == enabled)

    try:
        query = await filter_query_by_user_permissions(
            db, query, user_id, "mcp", MCPToolORM.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    result = await db.execute(
        query.order_by(MCPToolORM.created_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = result.scalars().all()

    return MCPToolListResponse(
        total=total or 0,
        items=items,
        page=page,
        page_size=page_size,
    )


@router.get("/{tool_id}", response_model=MCPToolResponse)
async def get_mcp_tool(tool_id: int, db: AsyncSession = Depends(get_db)):
    """获取MCP工具详情"""
    result = await db.execute(select(MCPToolORM).where(MCPToolORM.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="MCP工具不存在")
    return tool


@router.get("/{tool_id}/by-user", response_model=MCPToolResponse)
async def get_mcp_tool_for_user(
    tool_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取用户有权限的MCP工具详情"""
    result = await db.execute(select(MCPToolORM).where(MCPToolORM.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="MCP工具不存在")

    try:
        allowed = await has_user_permission(db, user_id, "mcp", tool_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if not allowed:
        raise HTTPException(status_code=403, detail="无权限访问该MCP工具")
    return tool


@router.post("/", response_model=MCPToolResponse)
async def create_mcp_tool(tool: MCPToolCreate, db: AsyncSession = Depends(get_db)):
    """创建MCP工具"""
    new_tool = MCPToolORM(**tool.model_dump())
    db.add(new_tool)
    await db.commit()
    await db.refresh(new_tool)
    return new_tool


@router.put("/{tool_id}", response_model=MCPToolResponse)
async def update_mcp_tool(
    tool_id: int, tool: MCPToolUpdate, db: AsyncSession = Depends(get_db)
):
    """更新MCP工具"""
    result = await db.execute(select(MCPToolORM).where(MCPToolORM.id == tool_id))
    db_tool = result.scalar_one_or_none()
    if not db_tool:
        raise HTTPException(status_code=404, detail="MCP工具不存在")

    update_data = tool.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tool, key, value)

    await db.commit()
    await db.refresh(db_tool)
    return db_tool


@router.delete("/{tool_id}")
async def delete_mcp_tool(tool_id: int, db: AsyncSession = Depends(get_db)):
    """删除MCP工具"""
    result = await db.execute(select(MCPToolORM).where(MCPToolORM.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="MCP工具不存在")

    await db.delete(tool)
    await db.commit()
    return {"message": "删除成功", "tool_id": tool_id}
