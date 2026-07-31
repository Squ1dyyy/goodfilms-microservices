import json
from typing import Optional

from monorepo.shared.repository.redis_repository import GenericRedisRepository
from movie.app.schemas.genre import GenreSchema


class GenreRedisRepository(GenericRedisRepository[GenreSchema]):
    prefix = "genre:"
    model_class = GenreSchema

    _LIST_KEY = "genre:list:all"

    async def save_genres_list(self, data: list[GenreSchema], ttl: int) -> None:
        raw = json.dumps([item.model_dump() for item in data])
        await self.set(self._LIST_KEY, raw, ttl=ttl)

    async def get_genres_list(self) -> Optional[list[GenreSchema]]:
        raw = await self.get(self._LIST_KEY)
        if raw is None:
            return None
        return [GenreSchema.model_validate(item) for item in json.loads(raw)]

    async def invalidate_genres_list(self) -> None:
        await self.delete(self._LIST_KEY)
