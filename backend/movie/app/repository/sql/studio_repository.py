from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie.models.items import StudiosModel


async def get_all_studios(session: AsyncSession) -> list[StudiosModel]:
    result = await session.execute(select(StudiosModel))
    return list(result.scalars().all())


async def get_or_create_studio(session: AsyncSession, name: str) -> StudiosModel:
    result = await session.execute(
        select(StudiosModel).where(StudiosModel.name == name)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    new_studio = StudiosModel(name=name)
    session.add(new_studio)
    await session.commit()
    await session.refresh(new_studio)
    return new_studio


async def patch_studio(
    session: AsyncSession, id: int, name: str
) -> Optional[StudiosModel]:
    result = await session.execute(select(StudiosModel).where(StudiosModel.id == id))
    existing = result.scalar_one_or_none()
    if existing is None:
        return None

    existing.name = name
    session.add(existing)
    await session.commit()
    await session.refresh(existing)
    return existing


async def delete_studio(session: AsyncSession, id: int) -> Optional[StudiosModel]:
    result = await session.execute(select(StudiosModel).where(StudiosModel.id == id))
    existing = result.scalar_one_or_none()
    if existing is None:
        return None

    await session.delete(existing)
    await session.commit()
    return existing
