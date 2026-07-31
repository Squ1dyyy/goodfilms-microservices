import json
from typing import Optional, List
from pydantic import TypeAdapter
from redis.asyncio import Redis

from monorepo.shared.repository.redis_repository import BaseRedisRepository
from recomendations.app.schemas.recommendation import MovieListItemSchema

_similar_movies_adapter: TypeAdapter[List[MovieListItemSchema]] = TypeAdapter(List[MovieListItemSchema])


class RecommendationRedisRepository(BaseRedisRepository):
    _SIMILAR_PREFIX = "similar_movies:"

    def _similar_key(self, movie_id: int) -> str:
        return f"{self._SIMILAR_PREFIX}{movie_id}"

    async def save_similar_movies(self, movie_id: int, data: List[MovieListItemSchema], ttl: int) -> None:
        key = self._similar_key(movie_id)
        serialized = _similar_movies_adapter.dump_json(data).decode("utf-8")
        await self.set(key, serialized, ttl=ttl)

    async def get_similar_movies(self, movie_id: int) -> Optional[List[MovieListItemSchema]]:
        key = self._similar_key(movie_id)
        raw = await self.get(key)
        if not raw:
            return None
        return _similar_movies_adapter.validate_json(raw)

    async def invalidate_similar_movies(self, movie_id: int) -> None:
        key = self._similar_key(movie_id)
        await self.delete(key)
