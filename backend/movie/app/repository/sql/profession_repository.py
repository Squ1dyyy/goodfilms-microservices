from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie.models.items import ProfessionsModel


async def get_all_professions(session: AsyncSession) -> list[ProfessionsModel]:
    result = await session.execute(select(ProfessionsModel))
    return list(result.scalars().all())


async def get_or_create_profession(
    session: AsyncSession, name: str
) -> ProfessionsModel:
    result = await session.execute(
        select(ProfessionsModel).where(ProfessionsModel.name == name)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    new_profession = ProfessionsModel(name=name)
    session.add(new_profession)
    await session.commit()
    await session.refresh(new_profession)
    return new_profession


async def patch_profession(
    session: AsyncSession, id: int, name: str
) -> Optional[ProfessionsModel]:
    result = await session.execute(
        select(ProfessionsModel).where(ProfessionsModel.id == id)
    )
    existing = result.scalar_one_or_none()
    if existing is None:
        return None

    existing.name = name
    session.add(existing)
    await session.commit()
    await session.refresh(existing)
    return existing


async def delete_profession(
    session: AsyncSession, id: int
) -> Optional[ProfessionsModel]:
    result = await session.execute(
        select(ProfessionsModel).where(ProfessionsModel.id == id)
    )
    existing = result.scalar_one_or_none()
    if existing is None:
        return None

    await session.delete(existing)
    await session.commit()
    return existing
