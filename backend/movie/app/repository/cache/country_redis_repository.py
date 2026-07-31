import json
from typing import Optional

from monorepo.shared.repository.redis_repository import GenericRedisRepository
from movie.app.schemas.country import CountrySchema


class CountryRedisRepository(GenericRedisRepository[CountrySchema]):
    prefix = "country:"
    model_class = CountrySchema

    _LIST_KEY = "country:list:all"

    async def save_countries_list(self, data: list[CountrySchema], ttl: int) -> None:
        raw = json.dumps([item.model_dump() for item in data])
        await self.set(self._LIST_KEY, raw, ttl=ttl)

    async def get_countries_list(self) -> Optional[list[CountrySchema]]:
        raw = await self.get(self._LIST_KEY)
        if raw is None:
            return None
        return [CountrySchema.model_validate(item) for item in json.loads(raw)]

    async def invalidate_countries_list(self) -> None:
        await self.delete(self._LIST_KEY)
