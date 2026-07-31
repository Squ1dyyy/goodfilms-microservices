from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie.models.items import GenresModel


async def get_all_genres(session: AsyncSession) -> Sequence[GenresModel]:
    all_genres = await session.execute(select(GenresModel))
    return all_genres.scalars().all()


async def get_or_create_genre(session: AsyncSession, genre_name: str) -> GenresModel:
    result = await session.execute(
        select(GenresModel).where(GenresModel.name == genre_name)
    )
    existing_genre = result.scalar_one_or_none()

    if existing_genre:
        return existing_genre

    new_genre = GenresModel(name=genre_name)
    session.add(new_genre)
    await session.commit()
    await session.refresh(new_genre)
    return new_genre


async def patch_genre(
    session: AsyncSession, id: int, new_genre_name: str
) -> Optional[GenresModel]:
    result = await session.execute(select(GenresModel).where(GenresModel.id == id))
    existing_genre = result.scalar_one_or_none()

    if existing_genre is None:
        return

    existing_genre.name = new_genre_name
    session.add(existing_genre)
    await session.commit()
    await session.refresh(existing_genre)
    return existing_genre


async def delete_genre(session: AsyncSession, id: int) -> Optional[GenresModel]:
    result = await session.execute(select(GenresModel).where(GenresModel.id == id))
    existing_genre = result.scalar_one_or_none()
    if existing_genre is None:
        return

    await session.delete(existing_genre)
    await session.commit()
    return existing_genre
