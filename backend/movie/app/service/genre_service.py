from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from movie.app.repository.sql import genre_repository as genre_db
from movie.app.repository.cache.genre_redis_repository import GenreRedisRepository
from movie.app.schemas.genre import GenreSchema
from movie.exception.exceptions import NotFound

_LIST_TTL = 60 * 60 * 24


class GenreService:
    def __init__(self, session: AsyncSession, cache: GenreRedisRepository):
        self.session = session
        self.cache = cache

    async def get_genres(self) -> list[GenreSchema]:
        cached = await self.cache.get_genres_list()
        if cached:
            return cached

        genres = await genre_db.get_all_genres(self.session)
        genres = [GenreSchema.model_validate(g) for g in genres]
        await self.cache.save_genres_list(genres, _LIST_TTL)
        return genres

    async def create_genre(self, genre: str) -> None:
        await genre_db.get_or_create_genre(self.session, genre)
        await self.cache.invalidate_genres_list()

    async def patch_genre(self, id: int, genre: str) -> None:
        updated_genre = await genre_db.patch_genre(self.session, id, genre)
        if updated_genre is None:
            raise NotFound()
        await self.cache.invalidate_genres_list()

    async def delete_genre(self, id: int) -> None:
        deleted_genre = await genre_db.delete_genre(self.session, id)
        if deleted_genre is None:
            raise NotFound()
        await self.cache.invalidate_genres_list()
