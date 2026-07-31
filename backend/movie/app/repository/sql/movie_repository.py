from typing import Optional
import re

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from movie.app.schemas.movie import (
    MovieQueryParams,
    CreateMovieSchema,
    UpdateMovieSchema,
)
from movie.models.items import (
    MoviesModel,
    GenresModel,
    StudiosModel,
    CountriesModel,
    MoviePersonsModel,
    KeywordsModel,
    MediaTypesModel,
)


async def get_films_by_ids(session: AsyncSession, ids: list[int]) -> list[MoviesModel]:
    if not ids:
        return []
    stmt = (
        select(MoviesModel)
        .options(
            selectinload(MoviesModel.genres),
            selectinload(MoviesModel.media_type_rel),
        )
        .where(MoviesModel.id.in_(ids))
    )
    result = await session.execute(stmt)
    movies_map = {m.id: m for m in result.scalars().all()}
    return [movies_map[id_] for id_ in ids if id_ in movies_map]


async def get_films(
    session: AsyncSession,
    params: MovieQueryParams,
    limit: int,
    page: int,
) -> tuple[list[MoviesModel], int]:
    offset = (page - 1) * limit

    id_stmt = select(MoviesModel.id).where(MoviesModel.title.op("~")("[а-яА-ЯёЁ]"))

    if params.genre_id is not None:
        id_stmt = id_stmt.where(
            MoviesModel.genres.any(GenresModel.id == params.genre_id)
        )
    if params.genre_name is not None:
        id_stmt = id_stmt.where(
            MoviesModel.genres.any(GenresModel.name.ilike(f"%{params.genre_name}%"))
        )
    if params.media_type is not None:
        id_stmt = id_stmt.where(
            MoviesModel.media_type_rel.has(MediaTypesModel.name == params.media_type)
        )
    if params.is_adult is not None:
        id_stmt = id_stmt.where(MoviesModel.is_adult == params.is_adult)
    if params.year_from is not None:
        id_stmt = id_stmt.where(MoviesModel.release_year >= params.year_from)
    if params.year_to is not None:
        id_stmt = id_stmt.where(MoviesModel.release_year <= params.year_to)
    if params.imdb_rating_from is not None:
        id_stmt = id_stmt.where(MoviesModel.imdb_rating >= params.imdb_rating_from)
    if params.imdb_rating_to is not None:
        id_stmt = id_stmt.where(MoviesModel.imdb_rating <= params.imdb_rating_to)
    if params.imdb_votes_from is not None:
        id_stmt = id_stmt.where(MoviesModel.imdb_votes >= params.imdb_votes_from)
    if params.tmdb_rating_from is not None:
        id_stmt = id_stmt.where(MoviesModel.tmdb_rating >= params.tmdb_rating_from)
    if params.tmdb_rating_to is not None:
        id_stmt = id_stmt.where(MoviesModel.tmdb_rating <= params.tmdb_rating_to)
    if params.tmdb_votes_from is not None:
        id_stmt = id_stmt.where(MoviesModel.tmdb_votes >= params.tmdb_votes_from)
    if params.search:
        escaped_search = re.sub(r'([\\^$.|?*+()\[\]{}])', r'\\\1', params.search)
        regex_pattern = f"\\m{escaped_search}"
        id_stmt = id_stmt.where(
            or_(
                MoviesModel.title.op("~*")(regex_pattern),
                MoviesModel.original_title.op("~*")(regex_pattern),
            )
        )

    total = (
        await session.scalar(select(func.count()).select_from(id_stmt.subquery())) or 0
    )

    is_random = (params.sort_by == "random") or (not params.sort_by)
    order_by_clauses = []
    if params.sort_by == "imdb_rating":
        order_by_clauses.append(MoviesModel.imdb_rating.desc().nulls_last())
        order_by_clauses.append(MoviesModel.id)
    elif params.sort_by == "imdb_votes":
        order_by_clauses.append(MoviesModel.imdb_votes.desc().nulls_last())
        order_by_clauses.append(MoviesModel.id)
    elif params.sort_by == "tmdb_rating":
        order_by_clauses.append(MoviesModel.tmdb_rating.desc().nulls_last())
        order_by_clauses.append(MoviesModel.id)
    elif params.sort_by == "tmdb_votes":
        order_by_clauses.append(MoviesModel.tmdb_votes.desc().nulls_last())
        order_by_clauses.append(MoviesModel.id)
    elif params.sort_by == "release_year_desc":
        order_by_clauses.append(MoviesModel.release_year.desc().nulls_last())
        order_by_clauses.append(MoviesModel.id)
    elif params.sort_by == "release_year_asc":
        order_by_clauses.append(MoviesModel.release_year.asc().nulls_last())
        order_by_clauses.append(MoviesModel.id)
    else:
        order_by_clauses.append(MoviesModel.poster_url.is_not(None).desc())
        order_by_clauses.append(func.random())

    paged_ids = await session.execute(
        id_stmt.order_by(*order_by_clauses).limit(limit).offset(offset)
    )
    ids = [row[0] for row in paged_ids.all()]

    if not ids:
        return [], total

    movies_stmt = (
        select(MoviesModel)
        .options(
            selectinload(MoviesModel.genres),
            selectinload(MoviesModel.studios),
            selectinload(MoviesModel.media_type_rel),
        )
        .where(MoviesModel.id.in_(ids))
        .order_by(*order_by_clauses)
    )
    movies = (await session.execute(movies_stmt)).scalars().all()

    return list(movies), total


async def get_film(
    session: AsyncSession,
    film_id: int,
) -> Optional[MoviesModel]:
    stmt = (
        select(MoviesModel)
        .options(
            selectinload(MoviesModel.genres),
            selectinload(MoviesModel.studios),
            selectinload(MoviesModel.countries),
            selectinload(MoviesModel.keywords),
            selectinload(MoviesModel.media_type_rel),
            selectinload(MoviesModel.movie_persons).selectinload(
                MoviePersonsModel.person
            ),
            selectinload(MoviesModel.movie_persons).selectinload(
                MoviePersonsModel.profession
            ),
        )
        .where(MoviesModel.id == film_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_movie(
    session: AsyncSession,
    data: CreateMovieSchema,
) -> Optional[MoviesModel]:
    genres = []
    if data.genre_ids:
        genres_result = await session.execute(
            select(GenresModel).where(GenresModel.id.in_(data.genre_ids))
        )
        genres = list(genres_result.scalars().all())

    studios = []
    if data.studio_ids:
        studios_result = await session.execute(
            select(StudiosModel).where(StudiosModel.id.in_(data.studio_ids))
        )
        studios = list(studios_result.scalars().all())

    countries = []
    if data.country_ids:
        countries_result = await session.execute(
            select(CountriesModel).where(CountriesModel.id.in_(data.country_ids))
        )
        countries = list(countries_result.scalars().all())

    keywords = []
    if data.keyword_ids:
        keywords_result = await session.execute(
            select(KeywordsModel).where(KeywordsModel.id.in_(data.keyword_ids))
        )
        keywords = list(keywords_result.scalars().all())

    movie_data = data.model_dump()
    for field in ["genre_ids", "studio_ids", "country_ids", "keyword_ids"]:
        movie_data.pop(field, None)

    new_movie = MoviesModel(
        **movie_data,
        genres=genres,
        studios=studios,
        countries=countries,
        keywords=keywords,
    )

    session.add(new_movie)
    await session.commit()

    session.expire_all()

    movie_with_relations = await get_film(session, new_movie.id)
    return movie_with_relations


async def patch_movie(
    session: AsyncSession,
    film_id: int,
    data: UpdateMovieSchema,
) -> Optional[MoviesModel]:
    movie = await get_film(session, film_id)
    if movie is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    relation_fields = ["genre_ids", "studio_ids", "country_ids", "keyword_ids"]
    for key, value in update_data.items():
        if key not in relation_fields:
            setattr(movie, key, value)

    if data.genre_ids is not None:
        if data.genre_ids:
            genres_result = await session.execute(
                select(GenresModel).where(GenresModel.id.in_(data.genre_ids))
            )
            movie.genres = list(genres_result.scalars().all())
        else:
            movie.genres = []

    if data.studio_ids is not None:
        if data.studio_ids:
            studios_result = await session.execute(
                select(StudiosModel).where(StudiosModel.id.in_(data.studio_ids))
            )
            movie.studios = list(studios_result.scalars().all())
        else:
            movie.studios = []

    if data.country_ids is not None:
        if data.country_ids:
            countries_result = await session.execute(
                select(CountriesModel).where(CountriesModel.id.in_(data.country_ids))
            )
            movie.countries = list(countries_result.scalars().all())
        else:
            movie.countries = []

    if data.keyword_ids is not None:
        if data.keyword_ids:
            keywords_result = await session.execute(
                select(KeywordsModel).where(KeywordsModel.id.in_(data.keyword_ids))
            )
            movie.keywords = list(keywords_result.scalars().all())
        else:
            movie.keywords = []

    session.add(movie)
    await session.commit()

    return await get_film(session, film_id)


async def delete_movie(
    session: AsyncSession,
    film_id: int,
) -> Optional[MoviesModel]:
    movie = await get_film(session, film_id)
    if movie is None:
        return None

    await session.delete(movie)
    await session.commit()
    return movie


async def add_movie_person(
    session: AsyncSession,
    movie_id: int,
    person_id: int,
    profession_id: int,
    character_name: Optional[str] = None,
    billing_order: Optional[int] = None,
) -> MoviePersonsModel:
    new_mp = MoviePersonsModel(
        movie_id=movie_id,
        person_id=person_id,
        profession_id=profession_id,
        character_name=character_name,
        billing_order=billing_order,
    )
    session.add(new_mp)
    await session.commit()
    return new_mp


async def patch_movie_person(
    session: AsyncSession,
    movie_id: int,
    movie_person_id: int,
    profession_id: Optional[int] = None,
    character_name: Optional[str] = None,
    billing_order: Optional[int] = None,
) -> Optional[MoviePersonsModel]:
    stmt = select(MoviePersonsModel).where(
        MoviePersonsModel.id == movie_person_id,
        MoviePersonsModel.movie_id == movie_id,
    )
    result = await session.execute(stmt)
    mp = result.scalar_one_or_none()
    if mp is None:
        return None

    if profession_id is not None:
        mp.profession_id = profession_id
    if character_name is not None:
        mp.character_name = character_name
    if billing_order is not None:
        mp.billing_order = billing_order

    session.add(mp)
    await session.commit()
    return mp


async def delete_movie_person(
    session: AsyncSession,
    movie_id: int,
    movie_person_id: int,
) -> Optional[MoviePersonsModel]:
    stmt = select(MoviePersonsModel).where(
        MoviePersonsModel.id == movie_person_id,
        MoviePersonsModel.movie_id == movie_id,
    )
    result = await session.execute(stmt)
    mp = result.scalar_one_or_none()
    if mp is None:
        return None

    await session.delete(mp)
    await session.commit()
    return mp
