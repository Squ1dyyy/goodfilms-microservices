from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from auth.app.repository.sql import user_repository
from auth.exception.exceptions import NotFound
from auth.models.items import UserModel


async def get_user(
    session: AsyncSession,
    user_id: int,
) -> UserModel:
    user_exist = await user_repository.get_by_id(session, user_id)
    if user_exist is None:
        raise NotFound()
    return user_exist


async def get_users(
    session: AsyncSession,
    limit: int,
    page: int,
    search: Optional[str] = None,
) -> tuple[list[UserModel], int]:
    return await user_repository.get_users(session, limit, page, search)


async def update_user(
    session: AsyncSession,
    user_id: int,
    is_active: Optional[bool] = None,
    role: Optional[str] = None,
) -> UserModel:
    user = await user_repository.update_user(session, user_id, is_active, role)
    if user is None:
        raise NotFound()
    return user


async def delete_user(
    session: AsyncSession,
    user_id: int,
) -> UserModel:
    user = await user_repository.delete_user(session, user_id)
    if user is None:
        raise NotFound()
    return user
