from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from movie.app.repository.sql import country_repository as country_db
from movie.app.repository.cache.country_redis_repository import CountryRedisRepository
from movie.app.schemas.country import CountrySchema
from movie.exception.exceptions import NotFound

_LIST_TTL = 60 * 60 * 24


class CountryService:
    def __init__(self, session: AsyncSession, cache: CountryRedisRepository):
        self.session = session
        self.cache = cache

    async def get_countries(self) -> list[CountrySchema]:
        cached = await self.cache.get_countries_list()
        if cached:
            return cached

        countries = await country_db.get_all_countries(self.session)
        countries = [CountrySchema.model_validate(c) for c in countries]
        await self.cache.save_countries_list(countries, _LIST_TTL)
        return countries

    async def create_country(self, country: str) -> None:
        await country_db.get_or_create_country(self.session, country)
        await self.cache.invalidate_countries_list()

    async def patch_country(self, id: int, country: str) -> None:
        updated_country = await country_db.patch_country(self.session, id, country)
        if updated_country is None:
            raise NotFound()
        await self.cache.invalidate_countries_list()

    async def delete_country(self, id: int) -> None:
        deleted_country = await country_db.delete_country(self.session, id)
        if deleted_country is None:
            raise NotFound()
        await self.cache.invalidate_countries_list()
