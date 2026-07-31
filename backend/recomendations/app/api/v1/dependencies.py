from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from recomendations.database.context import get_db, get_redis
from recomendations.app.service.recommendation_service import RecommendationService
from recomendations.app.repository.cache.recommendation_redis_repository import RecommendationRedisRepository

SessionDep = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[Redis, Depends(get_redis)]


async def get_recommendation_service(
    session: SessionDep,
    redis: RedisDep,
) -> RecommendationService:
    return RecommendationService(session=session, cache=RecommendationRedisRepository(redis))


RecommendationServiceDep = Annotated[
    RecommendationService, Depends(get_recommendation_service)
]

