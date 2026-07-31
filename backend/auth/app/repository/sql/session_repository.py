from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.items import SessionModel


async def get_sessions_by_user_agent(
    session: AsyncSession,
    user_id: int,
    user_agent: str,
) -> list[SessionModel]:
    result = await session.execute(
        select(SessionModel).where(
            SessionModel.user_id == user_id,
            SessionModel.user_agent == user_agent,
        ),
    )
    return list(result.scalars().all())


async def get_session_by_id(
    session: AsyncSession,
    session_id: int,
    user_id: int,
) -> SessionModel:
    result = await session.execute(
        select(SessionModel).where(
            SessionModel.id == session_id,
            SessionModel.user_id == user_id,
        ),
    )
    return result.scalars().one_or_none()


async def add_session(
    session: AsyncSession,
    session_model: SessionModel,
) -> None:
    session.add(session_model)


async def delete_session_by_token(
    session: AsyncSession,
    token_hash: str,
) -> None:
    result = await session.execute(
        select(SessionModel).where(SessionModel.token_hash == token_hash),
    )
    session_model = result.scalar_one_or_none()
    if session_model:
        await session.delete(session_model)


async def get_sessions(
    session: AsyncSession,
    user_id: int,
) -> Optional[list[SessionModel]]:
    result = await session.execute(
        select(SessionModel).where(SessionModel.user_id == user_id),
    )
    return list(result.scalars().all())


async def delete_sessions(
    session: AsyncSession,
    user_id: int,
) -> None:
    await session.execute(delete(SessionModel).where(SessionModel.user_id == user_id))
