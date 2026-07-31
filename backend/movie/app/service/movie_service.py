from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from movie.app.repository.sql import movie_repository as movie_db
from movie.app.repository.cache.movie_redis_repository import MovieRedisRepository
from movie.app.schemas.movie import (
    MovieListItemSchema,
    MovieDetailSchema,
    MovieQueryParams,
    CreateMovieSchema,
    UpdateMovieSchema,
    PersonInMovieSchema,
)
from movie.app.schemas.base import PaginatedResponseSchema
from movie.models.items import MoviesModel
from movie.exception.exceptions import NotFound

_FILMS_LIST_TTL = 300
_FILM_TTL = 60 * 60 * 24
_RANDOM_FILMS_TTL = 60 * 60 * 24


class MovieService:
    def __init__(self, session: AsyncSession, cache: MovieRedisRepository):
        self.session = session
        self.cache = cache

    _PROFESSION_ID_BUCKET = {1: "cast", 2: "directors", 3: "writers", 4: "producers"}
    _PROFESSION_NAME_BUCKET = (
        (("actor", "cast", "актёр", "актер", "актри"), "cast"),
        (("director", "режисс"), "directors"),
        (("writer", "scenar", "сценар", "сцена"), "writers"),
        (("producer", "продюс"), "producers"),
    )

    @classmethod
    def _classify_profession(cls, profession) -> Optional[str]:
        if profession is None:
            return None
        bucket = cls._PROFESSION_ID_BUCKET.get(getattr(profession, "id", None))
        if bucket:
            return bucket
        name = (getattr(profession, "name", "") or "").lower()
        for needles, target in cls._PROFESSION_NAME_BUCKET:
            if any(n in name for n in needles):
                return target
        return None

    def _map_movie_to_detail(self, film: MoviesModel) -> MovieDetailSchema:
        genres = [g.name for g in film.genres]
        studios = [s.name for s in film.studios]
        keywords = [k.name for k in film.keywords] if getattr(film, "keywords", None) else []

        cast = []
        directors = []
        writers = []
        producers = []

        movie_persons = film.movie_persons or []
        for mp in movie_persons:
            person_schema = PersonInMovieSchema(
                person_id=mp.person.id,
                full_name=mp.person.full_name,
                photo_url=mp.person.photo_url,
                character_name=mp.character_name,
                billing_order=mp.billing_order,
            )
            bucket = self._classify_profession(mp.profession)
            if bucket == "cast":
                cast.append(person_schema)
            elif bucket == "directors":
                directors.append(person_schema)
            elif bucket == "writers":
                writers.append(person_schema)
            elif bucket == "producers":
                producers.append(person_schema)

        return MovieDetailSchema(
            id=film.id,
            title=film.title,
            original_title=film.original_title,
            description=film.description or "",
            release_year=film.release_year or 0,
            poster_url=film.poster_url,
            backdrop_url=getattr(film, "backdrop_url", None),
            media_type=getattr(film, "media_type", None),
            is_adult=getattr(film, "is_adult", False) or False,
            imdb_id=film.imdb_id,
            imdb_rating=film.imdb_rating,
            imdb_votes=film.imdb_votes,
            tmdb_id=film.tmdb_id,
            tmdb_rating=film.tmdb_rating,
            tmdb_votes=film.tmdb_votes,
            trailer_url=film.trailer_url,
            genres=genres,
            studios=studios,
            keywords=keywords,
            cast=cast,
            directors=directors,
            writers=writers,
            producers=producers,
        )

    async def get_films(
        self,
        params: MovieQueryParams,
        limit: int,
        page: int,
    ) -> PaginatedResponseSchema[MovieListItemSchema]:
        filters = params.model_dump(exclude_none=True)
        is_random = (params.sort_by == "random") or (not params.sort_by)
        ttl = _RANDOM_FILMS_TTL if is_random else _FILMS_LIST_TTL

        cached = await self.cache.get_films_list(limit, page, filters)
        if cached:
            return cached

        movies, total = await movie_db.get_films(self.session, params, limit, page)
        films_list = PaginatedResponseSchema(
            items=[MovieListItemSchema.model_validate(m) for m in movies],
            total=total,
            page=page,
            limit=limit,
        )

        await self.cache.save_films_list(
            limit, page, films_list, ttl, filters
        )
        return films_list

    async def get_movies_by_ids(self, ids: list[int]) -> list[MovieListItemSchema]:
        if not ids:
            return []
        movies = await movie_db.get_films_by_ids(self.session, ids)
        return [MovieListItemSchema.model_validate(m) for m in movies]

    async def get_film(self, film_id: int) -> MovieDetailSchema:
        cached = await self.cache.get_film(film_id)
        if cached:
            return cached

        film = await movie_db.get_film(self.session, film_id)
        if film is None:
            raise NotFound()

        detail = self._map_movie_to_detail(film)
        await self.cache.save_film(film_id, detail, _FILM_TTL)
        return detail

    async def create_movie(self, data: CreateMovieSchema) -> MovieDetailSchema:
        film = await movie_db.create_movie(self.session, data)
        if film is None:
            raise NotFound()
        detail = self._map_movie_to_detail(film)
        await self.cache.invalidate_films_list()
        return detail

    async def patch_movie(
        self, film_id: int, data: UpdateMovieSchema
    ) -> MovieDetailSchema:
        film = await movie_db.patch_movie(self.session, film_id, data)
        if film is None:
            raise NotFound()
        detail = self._map_movie_to_detail(film)
        await self.cache.invalidate_film(film_id)
        await self.cache.invalidate_films_list()
        return detail

    async def delete_movie(self, film_id: int) -> MovieDetailSchema:
        film = await movie_db.delete_movie(self.session, film_id)
        if film is None:
            raise NotFound()
        detail = self._map_movie_to_detail(film)
        await self.cache.invalidate_film(film_id)
        await self.cache.invalidate_films_list()
        return detail

    async def add_movie_person(
        self,
        movie_id: int,
        person_id: int,
        profession_id: int,
        character_name: Optional[str] = None,
        billing_order: Optional[int] = None,
    ) -> MovieDetailSchema:
        mp = await movie_db.add_movie_person(
            self.session,
            movie_id,
            person_id,
            profession_id,
            character_name,
            billing_order,
        )
        film = await movie_db.get_film(self.session, movie_id)
        if film is None:
            raise NotFound()
        detail = self._map_movie_to_detail(film)
        await self.cache.invalidate_film(movie_id)
        await self.cache.invalidate_films_list()
        return detail

    async def patch_movie_person(
        self,
        movie_id: int,
        movie_person_id: int,
        profession_id: Optional[int] = None,
        character_name: Optional[str] = None,
        billing_order: Optional[int] = None,
    ) -> MovieDetailSchema:
        mp = await movie_db.patch_movie_person(
            self.session,
            movie_id,
            movie_person_id,
            profession_id,
            character_name,
            billing_order,
        )
        if mp is None:
            raise NotFound()
        film = await movie_db.get_film(self.session, movie_id)
        if film is None:
            raise NotFound()
        detail = self._map_movie_to_detail(film)
        await self.cache.invalidate_film(movie_id)
        await self.cache.invalidate_films_list()
        return detail

    async def delete_movie_person(
        self,
        movie_id: int,
        movie_person_id: int,
    ) -> tuple[MovieDetailSchema, int]:
        mp = await movie_db.delete_movie_person(self.session, movie_id, movie_person_id)
        if mp is None:
            raise NotFound()
        film = await movie_db.get_film(self.session, movie_id)
        if film is None:
            raise NotFound()
        detail = self._map_movie_to_detail(film)
        await self.cache.invalidate_film(movie_id)
        await self.cache.invalidate_films_list()
        return detail, mp.person_id
