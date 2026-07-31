import logging
from faststream.rabbit import RabbitRouter, RabbitExchange, RabbitQueue, ExchangeType
from recomendations.database.context import AsyncSessionLocal
from recomendations.app.service.recommendation_service import RecommendationService
from recomendations.app.schemas.recommendation import MovieCreatedEventSchema, MovieDeletedEventSchema

logger = logging.getLogger(__name__)
rabbit_router = RabbitRouter()




films_exchange = RabbitExchange(name="films", type=ExchangeType.TOPIC)
films_created_queue = RabbitQueue(
    name="recommendations-movie-created", routing_key="movie.created"
)
films_updated_queue = RabbitQueue(
    name="recommendations-movie-updated", routing_key="movie.updated"
)
films_deleted_queue = RabbitQueue(
    name="recommendations-movie-deleted", routing_key="movie.deleted"
)


async def upsert_movie_embedding(movie_id: int, movie_data: dict):
    async with AsyncSessionLocal() as session:
        service = RecommendationService(session)
        await service.upsert_movie_embedding(movie_id, movie_data)


@rabbit_router.subscriber(queue=films_created_queue, exchange=films_exchange)
async def handle_movie_created(data: MovieCreatedEventSchema):
    movie_data = {
        "title": data.title,
        "description": data.description,
        "release_year": data.release_year,
        "poster_url": data.poster_url,
        "genres": data.genres,
        "imdb_rating": data.imdb_rating
    }
    await upsert_movie_embedding(data.movie_id, movie_data)


@rabbit_router.subscriber(queue=films_updated_queue, exchange=films_exchange)
async def handle_movie_updated(data: MovieCreatedEventSchema):
    movie_data = {
        "title": data.title,
        "description": data.description,
        "release_year": data.release_year,
        "poster_url": data.poster_url,
        "genres": data.genres,
        "imdb_rating": data.imdb_rating
    }
    await upsert_movie_embedding(data.movie_id, movie_data)
    from recomendations.core import redis_config
    if redis_config.redis_client:
        try:
            await redis_config.redis_client.delete(f"similar_movies:{data.movie_id}")
        except Exception as e:
            logger.error(f"Failed to clear Redis cache for movie {data.movie_id}: {e}")


@rabbit_router.subscriber(queue=films_deleted_queue, exchange=films_exchange)
async def handle_movie_deleted(data: MovieDeletedEventSchema):
    async with AsyncSessionLocal() as session:
        service = RecommendationService(session)
        await service.delete_movie_embedding(data.movie_id)
    from recomendations.core import redis_config
    if redis_config.redis_client:
        try:
            await redis_config.redis_client.delete(f"similar_movies:{data.movie_id}")
        except Exception as e:
            logger.error(f"Failed to clear Redis cache for movie {data.movie_id}: {e}")

