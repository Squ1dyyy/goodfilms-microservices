from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from reviews.app.schemas.review import (
    PaginatedResponseSchema,
    ReviewResponseSchema,
    RatingSummarySchema,
)
from reviews.app.repository.sql.review_sql_repository import (
    create_review as create_sql_review,
    get_reviews_by_movie_id,
    get_review_by_id as get_sql_review_by_id,
    delete_review as delete_sql_review,
    upsert_rating as upsert_sql_rating,
    get_ratings_summary as get_sql_ratings_summary,
)
from reviews.app.repository.cache.review_redis_repository import ReviewRedisRepository

_REVIEWS_LIST_TTL = 300


class ReviewService:
    def __init__(self, session: AsyncSession, cache: ReviewRedisRepository):
        self.session = session
        self.cache = cache

    async def create_review(
        self, user_id: int, movie_id: int, review: str, username: Optional[str] = None
    ) -> ReviewResponseSchema:
        db_review = await create_sql_review(
            self.session, user_id, movie_id, review, username
        )
        await self.cache.invalidate_reviews_list(movie_id)
        return ReviewResponseSchema.model_validate(db_review)

    async def get_reviews(
        self, movie_id: int, last_id: Optional[int], limit: int
    ) -> PaginatedResponseSchema[ReviewResponseSchema]:
        cached = await self.cache.get_reviews_list(movie_id, last_id, limit)
        if cached:
            return cached

        db_reviews = await get_reviews_by_movie_id(
            self.session, movie_id, last_id, limit
        )
        items = [ReviewResponseSchema.model_validate(r) for r in db_reviews]
        next_cursor = items[-1].id if len(items) == limit else None

        result = PaginatedResponseSchema[ReviewResponseSchema](
            items=items,
            next_cursor=next_cursor,
            limit=limit,
        )

        await self.cache.save_reviews_list(
            movie_id, last_id, limit, result, _REVIEWS_LIST_TTL
        )
        return result

    async def get_review_by_id(self, review_id: int) -> Optional[ReviewResponseSchema]:
        db_review = await get_sql_review_by_id(self.session, review_id)
        if not db_review:
            return None
        return ReviewResponseSchema.model_validate(db_review)

    async def delete_review(self, review_id: int) -> bool:
        db_review = await get_sql_review_by_id(self.session, review_id)
        if not db_review:
            return False
        movie_id = db_review.movie_id
        await delete_sql_review(self.session, db_review)
        await self.cache.invalidate_reviews_list(movie_id)
        return True

    async def rate_movie(self, user_id: int, movie_id: int, rating: int) -> None:
        await upsert_sql_rating(self.session, user_id, movie_id, rating)
        await self.cache.invalidate_ratings_summary(movie_id)

    async def get_ratings_summary(self, movie_id: int) -> RatingSummarySchema:
        cached = await self.cache.get_ratings_summary(movie_id)
        if cached:
            return cached

        db_summary = await get_sql_ratings_summary(self.session, movie_id)
        result = RatingSummarySchema(**db_summary)

        await self.cache.save_ratings_summary(movie_id, result, ttl=300)
        return result
