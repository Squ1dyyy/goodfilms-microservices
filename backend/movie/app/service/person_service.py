from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from movie.app.repository.sql import person_repository as person_db
from movie.app.repository.cache.person_redis_repository import PersonRedisRepository
from movie.app.schemas.person import PersonSchema, PersonMoviesSchema
from movie.app.schemas.movie import MovieListItemSchema
from movie.app.schemas.base import PaginatedResponseSchema
from movie.exception.exceptions import NotFound

_MOVIES_TTL = 300


class PersonService:
    def __init__(self, session: AsyncSession, cache: PersonRedisRepository):
        self.session = session
        self.cache = cache

    async def get_persons(
        self,
        search: Optional[str],
        limit: int,
        page: int,
    ) -> PaginatedResponseSchema[PersonSchema]:
        filters = {"search": search} if search else {}
        cached = await self.cache.get_persons_list(limit, page, filters)
        if cached:
            return cached

        persons, total = await person_db.get_persons(self.session, search, limit, page)
        res = PaginatedResponseSchema(
            items=[PersonSchema.model_validate(p) for p in persons],
            total=total,
            page=page,
            limit=limit,
        )
        await self.cache.save_persons_list(limit, page, res, 300, filters)
        return res

    async def get_person(self, person_id: int) -> PersonSchema:
        cached = await self.cache.get_entity(person_id)
        if cached:
            return cached

        person = await person_db.get_person(self.session, person_id)
        if person is None:
            raise NotFound()
        return PersonSchema.model_validate(person)

    async def get_person_movies(
        self,
        person_id: int,
        limit: int,
        page: int,
    ) -> PersonMoviesSchema:
        cached = await self.cache.get_person_movies(person_id, limit, page)
        if cached:
            return cached

        person = await person_db.get_person(self.session, person_id)
        if person is None:
            raise NotFound()
        person_schema = PersonSchema.model_validate(person)

        movies, total = await person_db.get_person_movies(
            self.session, person_id, limit, page
        )

        result = PersonMoviesSchema(
            person=person_schema,
            movies=PaginatedResponseSchema(
                items=[MovieListItemSchema.model_validate(m) for m in movies],
                total=total,
                page=page,
                limit=limit,
            ),
        )

        await self.cache.save_person_movies(person_id, limit, page, result, _MOVIES_TTL)
        return result

    async def create_person(
        self,
        full_name: str,
        birth_date: Optional[date] = None,
        photo_url: Optional[str] = None,
    ) -> PersonSchema:
        person = await person_db.create_person(
            self.session, full_name, birth_date, photo_url
        )
        schema = PersonSchema.model_validate(person)
        await self.cache.invalidate_persons_list()
        return schema

    async def patch_person(
        self,
        person_id: int,
        full_name: Optional[str] = None,
        birth_date: Optional[date] = None,
        photo_url: Optional[str] = None,
    ) -> PersonSchema:
        person = await person_db.patch_person(
            self.session, person_id, full_name, birth_date, photo_url
        )
        if person is None:
            raise NotFound()
        schema = PersonSchema.model_validate(person)
        await self.cache.delete_entity(person_id)
        await self.cache.invalidate_person_movies(person_id)
        await self.cache.invalidate_persons_list()
        return schema

    async def delete_person(
        self,
        person_id: int,
    ) -> PersonSchema:
        person = await person_db.delete_person(self.session, person_id)
        if person is None:
            raise NotFound()
        schema = PersonSchema.model_validate(person)
        await self.cache.delete_entity(person_id)
        await self.cache.invalidate_person_movies(person_id)
        await self.cache.invalidate_persons_list()
        return schema
