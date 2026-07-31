from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from users.models.items import MovieBookmarkModel


async def add_bookmark(
    session: AsyncSession,
    user_id: int,
    movie_id: int,
) -> MovieBookmarkModel:
    query = (
        select(MovieBookmarkModel)
        .where(MovieBookmarkModel.user_id == user_id)
        .where(MovieBookmarkModel.movie_id == movie_id)
    )
    result = await session.execute(query)
    bookmark = result.scalar_one_or_none()
    if bookmark:
        return bookmark

    bookmark = MovieBookmarkModel(user_id=user_id, movie_id=movie_id)
    session.add(bookmark)
    await session.commit()
    return bookmark


async def remove_bookmark(
    session: AsyncSession,
    user_id: int,
    movie_id: int,
) -> bool:
    stmt = (
        delete(MovieBookmarkModel)
        .where(MovieBookmarkModel.user_id == user_id)
        .where(MovieBookmarkModel.movie_id == movie_id)
        .returning(MovieBookmarkModel.id)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one_or_none() is not None


async def get_bookmarks(
    session: AsyncSession,
    user_id: int,
) -> Sequence[int]:
    query = select(MovieBookmarkModel.movie_id).where(
        MovieBookmarkModel.user_id == user_id
    )
    result = await session.execute(query)
    return result.scalars().all()
