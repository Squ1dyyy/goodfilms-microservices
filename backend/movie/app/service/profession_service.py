from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from movie.app.repository.sql import profession_repository as profession_db
from movie.app.repository.cache.profession_redis_repository import (
    ProfessionRedisRepository,
)
from movie.app.schemas.profession import ProfessionSchema
from movie.exception.exceptions import NotFound

_LIST_TTL = 60 * 60 * 24


class ProfessionService:
    def __init__(self, session: AsyncSession, cache: ProfessionRedisRepository):
        self.session = session
        self.cache = cache

    async def get_professions(self) -> list[ProfessionSchema]:
        cached = await self.cache.get_professions_list()
        if cached:
            return cached

        professions = await profession_db.get_all_professions(self.session)
        professions = [ProfessionSchema.model_validate(p) for p in professions]
        await self.cache.save_professions_list(professions, _LIST_TTL)
        return professions

    async def create_profession(self, name: str) -> None:
        await profession_db.get_or_create_profession(self.session, name)
        await self.cache.invalidate_professions_list()

    async def patch_profession(self, id: int, name: str) -> None:
        updated = await profession_db.patch_profession(self.session, id, name)
        if updated is None:
            raise NotFound()
        await self.cache.invalidate_professions_list()

    async def delete_profession(self, id: int) -> None:
        deleted = await profession_db.delete_profession(self.session, id)
        if deleted is None:
            raise NotFound()
        await self.cache.invalidate_professions_list()
