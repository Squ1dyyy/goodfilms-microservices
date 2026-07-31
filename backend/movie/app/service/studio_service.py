from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from movie.app.repository.sql import studio_repository as studio_db
from movie.app.repository.cache.studio_redis_repository import StudioRedisRepository
from movie.app.schemas.studio import StudioSchema
from movie.exception.exceptions import NotFound

_LIST_TTL = 60 * 60 * 24


class StudioService:
    def __init__(self, session: AsyncSession, cache: StudioRedisRepository):
        self.session = session
        self.cache = cache

    async def get_studios(self) -> list[StudioSchema]:
        cached = await self.cache.get_studios_list()
        if cached:
            return cached

        studios = await studio_db.get_all_studios(self.session)
        studios = [StudioSchema.model_validate(s) for s in studios]
        await self.cache.save_studios_list(studios, _LIST_TTL)
        return studios

    async def create_studio(self, name: str) -> None:
        await studio_db.get_or_create_studio(self.session, name)
        await self.cache.invalidate_studios_list()

    async def patch_studio(self, id: int, name: str) -> None:
        updated = await studio_db.patch_studio(self.session, id, name)
        if updated is None:
            raise NotFound()
        await self.cache.invalidate_studios_list()

    async def delete_studio(self, id: int) -> None:
        deleted = await studio_db.delete_studio(self.session, id)
        if deleted is None:
            raise NotFound()
        await self.cache.invalidate_studios_list()
