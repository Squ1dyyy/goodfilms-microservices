import json
from typing import Optional

from monorepo.shared.repository.redis_repository import GenericRedisRepository
from movie.app.schemas.studio import StudioSchema


class StudioRedisRepository(GenericRedisRepository[StudioSchema]):
    prefix = "studio:"
    model_class = StudioSchema

    _LIST_KEY = "studio:list:all"

    async def save_studios_list(self, data: list[StudioSchema], ttl: int) -> None:
        raw = json.dumps([item.model_dump() for item in data])
        await self.set(self._LIST_KEY, raw, ttl=ttl)

    async def get_studios_list(self) -> Optional[list[StudioSchema]]:
        raw = await self.get(self._LIST_KEY)
        if raw is None:
            return None
        return [StudioSchema.model_validate(item) for item in json.loads(raw)]

    async def invalidate_studios_list(self) -> None:
        await self.delete(self._LIST_KEY)
