from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.items import UserModel


async def get_by_email(
    session: AsyncSession,
    email: str,
) -> Optional[UserModel]:
    stmt = select(UserModel).where(UserModel.email == email)
    return (await session.execute(stmt)).scalar_one_or_none()


async def get_by_id(
    session: AsyncSession,
    user_id: int,
) -> Optional[UserModel]:
    return await session.get(UserModel, user_id)


async def create_user(
    session: AsyncSession,
    user: UserModel,
) -> None:
    session.add(user)


async def get_users(
    session: AsyncSession,
    limit: int,
    page: int,
    search: Optional[str] = None,
) -> tuple[list[UserModel], int]:
    from sqlalchemy import func

    offset = (page - 1) * limit
    stmt = select(UserModel.id)
    if search:
        stmt = stmt.where(
            (UserModel.username.ilike(f"%{search}%"))
            | (UserModel.email.ilike(f"%{search}%"))
        )
    total = await session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    paged_ids = await session.execute(
        stmt.order_by(UserModel.id).limit(limit).offset(offset)
    )
    ids = [row[0] for row in paged_ids.all()]
    if not ids:
        return [], total
    users_stmt = select(UserModel).where(UserModel.id.in_(ids)).order_by(UserModel.id)
    users = (await session.execute(users_stmt)).scalars().all()
    return list(users), total


async def update_user(
    session: AsyncSession,
    user_id: int,
    is_active: Optional[bool] = None,
    role: Optional[str] = None,
) -> Optional[UserModel]:
    user = await get_by_id(session, user_id)
    if user is None:
        return None
    if is_active is not None:
        user.is_active = is_active
    if role is not None:
        user.role = role
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(
    session: AsyncSession,
    user_id: int,
) -> Optional[UserModel]:
    user = await get_by_id(session, user_id)
    if user is None:
        return None
    await session.delete(user)
    await session.commit()
    return user
