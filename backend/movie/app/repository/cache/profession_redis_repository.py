import json
from typing import Optional

from monorepo.shared.repository.redis_repository import GenericRedisRepository
from movie.app.schemas.profession import ProfessionSchema


class ProfessionRedisRepository(GenericRedisRepository[ProfessionSchema]):
    prefix = "profession:"
    model_class = ProfessionSchema

    _LIST_KEY = "profession:list:all"

    async def save_professions_list(
        self, data: list[ProfessionSchema], ttl: int
    ) -> None:
        raw = json.dumps([item.model_dump() for item in data])
        await self.set(self._LIST_KEY, raw, ttl=ttl)

    async def get_professions_list(self) -> Optional[list[ProfessionSchema]]:
        raw = await self.get(self._LIST_KEY)
        if raw is None:
            return None
        return [ProfessionSchema.model_validate(item) for item in json.loads(raw)]

    async def invalidate_professions_list(self) -> None:
        await self.delete(self._LIST_KEY)
