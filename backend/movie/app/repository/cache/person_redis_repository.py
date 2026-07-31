from typing import Optional

from monorepo.shared.repository.redis_repository import GenericRedisRepository
from movie.app.schemas.person import PersonSchema, PersonMoviesSchema
from movie.app.schemas.base import PaginatedResponseSchema


class PersonRedisRepository(GenericRedisRepository[PersonSchema]):
    prefix = "person:"
    model_class = PersonSchema

    _MOVIES_PREFIX = "person:movies:"

    def _movies_key(self, person_id: int, limit: int, page: int) -> str:
        return f"{self._MOVIES_PREFIX}{person_id}:{limit}:{page}"

    async def save_person_movies(
        self,
        person_id: int,
        limit: int,
        page: int,
        data: PersonMoviesSchema,
        ttl: int,
    ) -> None:
        key = self._movies_key(person_id, limit, page)
        await self.set(key, data.model_dump_json(), ttl=ttl)

    async def get_person_movies(
        self,
        person_id: int,
        limit: int,
        page: int,
    ) -> Optional[PersonMoviesSchema]:
        raw = await self.get(self._movies_key(person_id, limit, page))
        if not raw:
            return None
        return PersonMoviesSchema.model_validate_json(raw)

    async def invalidate_person_movies(self, person_id: int) -> None:
        keys = await self.redis.keys(f"{self._MOVIES_PREFIX}{person_id}:*")
        if keys:
            await self.delete(keys)

    _PERSONS_LIST_PREFIX = "persons:list:"

    def _persons_list_key(self, limit: int, page: int, filters: dict) -> str:
        import hashlib
        import json

        filters_hash = hashlib.md5(
            json.dumps(filters, sort_keys=True).encode()
        ).hexdigest()
        return f"{self._PERSONS_LIST_PREFIX}{limit}:{page}:{filters_hash}"

    async def save_persons_list(
        self,
        limit: int,
        page: int,
        data: PaginatedResponseSchema[PersonSchema],
        ttl: int,
        filters: dict,
    ) -> None:
        key = self._persons_list_key(limit, page, filters)
        await self.set(key, data.model_dump_json(), ttl=ttl)

    async def get_persons_list(
        self,
        limit: int,
        page: int,
        filters: dict,
    ) -> Optional[PaginatedResponseSchema[PersonSchema]]:
        key = self._persons_list_key(limit, page, filters)
        raw = await self.get(key)
        if not raw:
            return None
        from pydantic import TypeAdapter
        from movie.app.schemas.base import PaginatedResponseSchema

        adapter = TypeAdapter(PaginatedResponseSchema[PersonSchema])
        return adapter.validate_json(raw)

    async def invalidate_persons_list(self) -> None:
        keys = await self.redis.keys(f"{self._PERSONS_LIST_PREFIX}*")
        if keys:
            await self.delete(keys)
