import hashlib
import json
from typing import Optional

from pydantic import TypeAdapter

from monorepo.shared.repository.redis_repository import BaseRedisRepository
from movie.app.schemas.movie import (
    MovieDetailSchema,
    MovieListItemSchema,
)
from movie.app.schemas.base import PaginatedResponseSchema


_films_list_adapter: TypeAdapter[PaginatedResponseSchema[MovieListItemSchema]] = (
    TypeAdapter(PaginatedResponseSchema[MovieListItemSchema])
)


class MovieRedisRepository(BaseRedisRepository):
    _FILM_PREFIX = "film:"
    _FILM_LIST_PREFIX = "films:list:"

    def _films_list_key(self, limit: int, page: int, filters: dict) -> str:
        filters_hash = hashlib.md5(
            json.dumps(filters, sort_keys=True).encode()
        ).hexdigest()
        return f"{self._FILM_LIST_PREFIX}{limit}:{page}:{filters_hash}"

    async def save_films_list(
        self,
        limit: int,
        page: int,
        data: PaginatedResponseSchema[MovieListItemSchema],
        ttl: int,
        filters: dict,
    ) -> None:
        key = self._films_list_key(limit, page, filters)
        await self.set(key, data.model_dump_json(), ttl=ttl)

    async def get_films_list(
        self,
        limit: int,
        page: int,
        filters: dict,
    ) -> Optional[PaginatedResponseSchema[MovieListItemSchema]]:
        key = self._films_list_key(limit, page, filters)
        raw = await self.get(key)
        if not raw:
            return None
        return _films_list_adapter.validate_json(raw)

    async def save_film(self, film_id: int, data: MovieDetailSchema, ttl: int) -> None:
        await self.set(f"{self._FILM_PREFIX}{film_id}", data.model_dump_json(), ttl=ttl)

    async def get_film(self, film_id: int) -> Optional[MovieDetailSchema]:
        raw = await self.get(f"{self._FILM_PREFIX}{film_id}")
        if not raw:
            return None
        return MovieDetailSchema.model_validate_json(raw)

    async def invalidate_film(self, film_id: int) -> None:
        await self.delete(f"{self._FILM_PREFIX}{film_id}")

    async def invalidate_films_list(self) -> None:
        keys = await self.redis.keys(f"{self._FILM_LIST_PREFIX}*")
        if keys:
            await self.delete(keys)
