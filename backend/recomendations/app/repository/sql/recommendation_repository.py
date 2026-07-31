from typing import Optional, List, Tuple
from sqlalchemy import select, delete, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from recomendations.models import MovieEmbeddingModel


async def get_by_id(session: AsyncSession, movie_id: int) -> Optional[MovieEmbeddingModel]:
    stmt = select(MovieEmbeddingModel).where(MovieEmbeddingModel.movie_id == movie_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def upsert(
    session: AsyncSession,
    movie_id: int,
    title: str,
    description: Optional[str],
    release_year: Optional[int],
    poster_url: Optional[str],
    genres: Optional[str],
    description_vector: Optional[List[float]],
    original_title: Optional[str] = None,
    imdb_id: Optional[str] = None,
    imdb_rating: Optional[float] = None,
    imdb_votes: Optional[int] = None,
    tmdb_id: Optional[int] = None,
    tmdb_rating: Optional[float] = None,
    tmdb_votes: Optional[int] = None,
    media_type: Optional[str] = None,
) -> MovieEmbeddingModel:
    record = await get_by_id(session, movie_id)
    if record:
        record.title = title
        record.original_title = original_title
        record.description = description
        record.release_year = release_year
        record.poster_url = poster_url
        record.genres = genres
        if description_vector is not None:
            record.description_vector = description_vector
        record.imdb_id = imdb_id
        record.imdb_rating = imdb_rating
        record.imdb_votes = imdb_votes
        record.tmdb_id = tmdb_id
        record.tmdb_rating = tmdb_rating
        record.tmdb_votes = tmdb_votes
        record.media_type = media_type
    else:
        record = MovieEmbeddingModel(
            movie_id=movie_id,
            title=title,
            original_title=original_title,
            description=description,
            release_year=release_year,
            poster_url=poster_url,
            genres=genres,
            description_vector=description_vector,
            imdb_id=imdb_id,
            imdb_rating=imdb_rating,
            imdb_votes=imdb_votes,
            tmdb_id=tmdb_id,
            tmdb_rating=tmdb_rating,
            tmdb_votes=tmdb_votes,
            media_type=media_type,
        )
        session.add(record)
    return record


async def delete_embedding(session: AsyncSession, movie_id: int) -> None:
    stmt = delete(MovieEmbeddingModel).where(MovieEmbeddingModel.movie_id == movie_id)
    await session.execute(stmt)


async def get_unencoded(session: AsyncSession, limit: int = 50) -> List[MovieEmbeddingModel]:
    stmt = (
        select(MovieEmbeddingModel)
        .where(
            MovieEmbeddingModel.description.isnot(None),
            MovieEmbeddingModel.description != "",
            MovieEmbeddingModel.description_vector.is_(None),
        )
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_similar_movies(
    session: AsyncSession,
    movie_id: int,
    target_vector: List[float],
    limit: int = 20,
) -> List[MovieEmbeddingModel]:
    similarity = MovieEmbeddingModel.description_vector.cosine_distance(target_vector)

    items_stmt = (
        select(MovieEmbeddingModel)
        .where(
            MovieEmbeddingModel.movie_id != movie_id,
            MovieEmbeddingModel.description_vector.isnot(None),
            MovieEmbeddingModel.title.op("~")("[а-яА-ЯёЁ]"),
        )
        .order_by(similarity)
        .limit(limit)
    )
    result = await session.execute(items_stmt)
    items = result.scalars().all()

    return list(items)


async def get_by_ids(session: AsyncSession, movie_ids: List[int]) -> List[MovieEmbeddingModel]:
    if not movie_ids:
        return []
    stmt = select(MovieEmbeddingModel).where(MovieEmbeddingModel.movie_id.in_(movie_ids))
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_similar_movies_custom(
    session: AsyncSession,
    target_vector: List[float],
    exclude_ids: List[int],
    genres: List[str],
    release_year: Optional[int],
    release_year_from: Optional[int] = None,
    release_year_to: Optional[int] = None,
    imdb_rating_from: Optional[float] = None,
    media_type: Optional[str] = None,
    limit: int = 20,
) -> List[MovieEmbeddingModel]:
    similarity = MovieEmbeddingModel.description_vector.cosine_distance(target_vector)

    stmt = select(MovieEmbeddingModel).where(
        MovieEmbeddingModel.description_vector.isnot(None),
        MovieEmbeddingModel.title.op("~")("[а-яА-ЯёЁ]"),
    )

    if exclude_ids:
        stmt = stmt.where(MovieEmbeddingModel.movie_id.notin_(exclude_ids))

    if release_year:
        stmt = stmt.where(MovieEmbeddingModel.release_year == release_year)

    if release_year_from:
        stmt = stmt.where(MovieEmbeddingModel.release_year >= release_year_from)

    if release_year_to:
        stmt = stmt.where(MovieEmbeddingModel.release_year <= release_year_to)

    if imdb_rating_from is not None:
        stmt = stmt.where(MovieEmbeddingModel.imdb_rating >= imdb_rating_from)

    if media_type:
        if media_type == "tv":
            stmt = stmt.where(MovieEmbeddingModel.media_type.in_(["tv", "tv_season", "tv_episode", "tv_series", "series"]))
        else:
            stmt = stmt.where(MovieEmbeddingModel.media_type == media_type)

    if genres:
        genre_filters = []
        for g in genres:
            genre_filters.append(MovieEmbeddingModel.genres.ilike(f"%{g}%"))
        stmt = stmt.where(or_(*genre_filters))

    stmt = stmt.order_by(similarity).limit(limit)
    result = await session.execute(stmt)
    items = result.scalars().all()

    return list(items)


async def get_random_films(
    session: AsyncSession,
    limit: int = 10,
) -> List[MovieEmbeddingModel]:
    stmt = select(MovieEmbeddingModel).order_by(func.random()).limit(limit)
    result = await session.execute(stmt)
    items = result.scalars().all()
    return list(items)
