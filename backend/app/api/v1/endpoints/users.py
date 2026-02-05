from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select, func, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from passlib.context import CryptContext

from app.core.database import get_db
from app.db.models import UserORM, UserResourcePermissionORM
from app.models.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserPermissionUpdate,
)

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

RESOURCE_TYPE_MAP = {
    "expert": "expert_ids",
    "subagent": "subagent_ids",
    "mcp": "mcp_ids",
    "skill": "skill_ids",
    "knowledge": "knowledge_ids",
    "model": "model_ids",
    "knowledge_graph": "knowledge_graph_ids",
}


def hash_password(password: str) -> str:
    """哈希密码，自动截断超长密码"""
    # bcrypt 限制密码长度为 72 字节
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return pwd_context.hash(password_bytes.decode('utf-8', errors='ignore'))


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """获取用户列表"""
    query = select(UserORM)

    if keyword:
        query = query.where(
            or_(
                UserORM.username.ilike(f"%{keyword}%"),
                UserORM.email.ilike(f"%{keyword}%"),
                UserORM.real_name.ilike(f"%{keyword}%"),
            )
        )

    if role:
        query = query.where(UserORM.role == role)

    if status:
        query = query.where(UserORM.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    result = await db.execute(
        query.order_by(UserORM.created_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = result.scalars().all()

    return UserListResponse(
        total=total or 0,
        items=items,
        page=page,
        page_size=page_size,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户详情"""
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """创建用户"""
    # 检查用户名是否存在
    exists_result = await db.execute(
        select(UserORM).where(UserORM.username == user.username)
    )
    if exists_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否存在
    if user.email:
        email_result = await db.execute(
            select(UserORM).where(UserORM.email == user.email)
        )
        if email_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="邮箱已存在")

    new_user = UserORM(
        username=user.username,
        password_hash=hash_password(user.password),
        email=user.email,
        phone=user.phone,
        real_name=user.real_name,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_data = user.model_dump(exclude_unset=True)
    
    # 如果更新密码，需要hash
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """删除用户"""
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    await db.delete(user)
    await db.commit()
    return {"message": "删除成功", "user_id": user_id}


@router.get("/{user_id}/permissions")
async def get_user_permissions(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户权限"""
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    permissions = {key: [] for key in RESOURCE_TYPE_MAP.values()}
    result = await db.execute(
        select(UserResourcePermissionORM).where(UserResourcePermissionORM.user_id == user_id)
    )
    rows = result.scalars().all()
    for row in rows:
        field_name = RESOURCE_TYPE_MAP.get(row.resource_type)
        if field_name is not None:
            permissions[field_name].append(row.resource_id)

    return permissions


@router.put("/{user_id}/permissions")
async def update_user_permissions(
    user_id: int, permissions: UserPermissionUpdate, db: AsyncSession = Depends(get_db)
):
    """更新用户权限"""
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_data = permissions.model_dump(exclude_unset=True)

    for resource_type, field_name in RESOURCE_TYPE_MAP.items():
        if field_name not in update_data:
            continue
        resource_ids = update_data.get(field_name) or []

        await db.execute(
            delete(UserResourcePermissionORM).where(
                UserResourcePermissionORM.user_id == user_id,
                UserResourcePermissionORM.resource_type == resource_type,
            )
        )

        new_rows = [
            UserResourcePermissionORM(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                permission_level="read",
            )
            for resource_id in resource_ids
        ]
        if new_rows:
            db.add_all(new_rows)

    await db.commit()
    return {"message": "权限更新成功", "user_id": user_id}

