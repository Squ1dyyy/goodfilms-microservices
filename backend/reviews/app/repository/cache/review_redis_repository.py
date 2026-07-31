from typing import Optional
from redis.asyncio import Redis
from pydantic import TypeAdapter
from monorepo.shared.repository.redis_repository import BaseRedisRepository
from reviews.app.schemas.review import (
    PaginatedResponseSchema,
    ReviewResponseSchema,
    RatingSummarySchema,
)

_reviews_list_adapter: TypeAdapter[PaginatedResponseSchema[ReviewResponseSchema]] = (
    TypeAdapter(PaginatedResponseSchema[ReviewResponseSchema])
)


class ReviewRedisRepository(BaseRedisRepository):
    _REVIEWS_LIST_PREFIX = "reviews:list:"

    def _reviews_list_key(
        self, movie_id: int, last_id: Optional[int], limit: int
    ) -> str:
        return f"{self._REVIEWS_LIST_PREFIX}{movie_id}:{last_id}:{limit}"

    async def save_reviews_list(
        self,
        movie_id: int,
        last_id: Optional[int],
        limit: int,
        data: PaginatedResponseSchema[ReviewResponseSchema],
        ttl: int,
    ) -> None:
        key = self._reviews_list_key(movie_id, last_id, limit)
        await self.set(key, data.model_dump_json(), ttl=ttl)

    async def get_reviews_list(
        self,
        movie_id: int,
        last_id: Optional[int],
        limit: int,
    ) -> Optional[PaginatedResponseSchema[ReviewResponseSchema]]:
        key = self._reviews_list_key(movie_id, last_id, limit)
        raw = await self.get(key)
        if not raw:
            return None
        return _reviews_list_adapter.validate_json(raw)

    async def invalidate_reviews_list(self, movie_id: int) -> None:
        keys = await self.redis.keys(f"{self._REVIEWS_LIST_PREFIX}{movie_id}:*")
        if keys:
            await self.delete(keys)

    _RATINGS_SUMMARY_PREFIX = "ratings:summary:"

    async def save_ratings_summary(
        self,
        movie_id: int,
        data: RatingSummarySchema,
        ttl: int,
    ) -> None:
        key = f"{self._RATINGS_SUMMARY_PREFIX}{movie_id}"
        await self.set(key, data.model_dump_json(), ttl=ttl)

    async def get_ratings_summary(
        self,
        movie_id: int,
    ) -> Optional[RatingSummarySchema]:
        key = f"{self._RATINGS_SUMMARY_PREFIX}{movie_id}"
        raw = await self.get(key)
        if not raw:
            return None
        return RatingSummarySchema.model_validate_json(raw)

    async def invalidate_ratings_summary(self, movie_id: int) -> None:
        key = f"{self._RATINGS_SUMMARY_PREFIX}{movie_id}"
        await self.delete(key)
