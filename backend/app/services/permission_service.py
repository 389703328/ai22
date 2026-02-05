from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserORM, UserResourcePermissionORM


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[UserORM]:
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    return result.scalar_one_or_none()


async def is_admin_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    return bool(user and user.role == "admin")


async def filter_query_by_user_permissions(
    db: AsyncSession,
    query,
    user_id: Optional[int],
    resource_type: str,
    id_column,
):
    if user_id is None:
        return query

    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("用户不存在")
    if user.role == "admin":
        return query

    permission_subquery = (
        select(UserResourcePermissionORM.resource_id)
        .where(
            UserResourcePermissionORM.user_id == user_id,
            UserResourcePermissionORM.resource_type == resource_type,
        )
        .subquery()
    )
    return query.where(id_column.in_(select(permission_subquery.c.resource_id)))


async def has_user_permission(
    db: AsyncSession,
    user_id: int,
    resource_type: str,
    resource_id: int,
) -> bool:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("用户不存在")
    if user.role == "admin":
        return True

    result = await db.execute(
        select(UserResourcePermissionORM.id).where(
            UserResourcePermissionORM.user_id == user_id,
            UserResourcePermissionORM.resource_type == resource_type,
            UserResourcePermissionORM.resource_id == resource_id,
        )
    )
    return result.scalar_one_or_none() is not None
