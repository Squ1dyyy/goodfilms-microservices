import asyncio
import logging
from typing import Optional, List, Dict

from celery import shared_task
from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType
from sqlalchemy import select

from movie.config import config
from movie.database.context import AsyncSessionLocal
from movie.models.items import MoviesModel, GenresModel

logger = logging.getLogger(__name__)

EMBEDDING_BATCH_SIZE = 20

films_exchange = RabbitExchange(name="films", type=ExchangeType.TOPIC)


async def fetch_movies_with_descriptions(
    batch_size: int = EMBEDDING_BATCH_SIZE,
    offset: int = 0,
) -> List[Dict]:
    """Fetch movies that have non-empty descriptions from movie_db."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(MoviesModel)
            .where(
                MoviesModel.description.isnot(None),
                MoviesModel.description != "",
            )
            .order_by(MoviesModel.id.asc())
            .offset(offset)
            .limit(batch_size)
        )
        result = await session.execute(stmt)
        movies = result.scalars().all()

        movie_dicts = []
        for movie in movies:
            genres_stmt = (
                select(GenresModel.name)
                .join(GenresModel.movies)
                .where(MoviesModel.id == movie.id)
            )
            genres_result = await session.execute(genres_stmt)
            genre_names = [row[0] for row in genres_result.all()]

            movie_dicts.append({
                "movie_id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "release_year": movie.release_year,
                "poster_url": movie.poster_url,
                "genres": genre_names,
                "imdb_rating": movie.imdb_rating,
            })
        return movie_dicts


async def publish_movies_batch_to_recommendations(movies: List[Dict]) -> None:
    """Publish a batch of movies to RabbitMQ for the recommendations service."""
    if not movies:
        return

    broker = RabbitBroker(config.RABBIT_BROKER_URL)
    async with broker:
        for movie in movies:
            try:
                await broker.publish(
                    message={
                        "movie_id": movie["movie_id"],
                        "title": movie["title"],
                        "description": movie.get("description"),
                        "release_year": movie.get("release_year"),
                        "poster_url": movie.get("poster_url"),
                        "genres": movie.get("genres") or [],
                        "imdb_rating": movie.get("imdb_rating"),
                    },
                    exchange=films_exchange,
                    routing_key="movie.updated",
                )
                logger.debug(
                    f"Published embedding event for movie_id={movie['movie_id']} "
                    f"'{movie['title']}'"
                )
            except Exception as e:
                logger.error(
                    f"Failed to publish embedding event for movie_id={movie['movie_id']}: {e}"
                )

    logger.info(f"Published {len(movies)} movie events to recommendations service.")


async def run_sync_embeddings_pipeline(
    batch_size: int = EMBEDDING_BATCH_SIZE,
    max_items: Optional[int] = None,
) -> int:
    """
    Main pipeline: reads all movies with descriptions from movie_db in batches
    and publishes RabbitMQ events to the recommendations microservice so it
    can generate and store description_vector embeddings.
    """
    total_published = 0
    offset = 0

    while True:
        current_batch_size = batch_size
        if max_items is not None:
            remaining = max_items - total_published
            if remaining <= 0:
                break
            current_batch_size = min(batch_size, remaining)

        movies = await fetch_movies_with_descriptions(
            batch_size=current_batch_size,
            offset=offset,
        )

        if not movies:
            logger.info("No more movies with descriptions found. Sync complete.")
            break

        logger.info(
            f"Publishing batch of {len(movies)} movies to recommendations "
            f"(offset={offset})..."
        )
        await publish_movies_batch_to_recommendations(movies)

        total_published += len(movies)
        offset += len(movies)

        if len(movies) < current_batch_size:
            break

    logger.info(
        f"Embedding sync pipeline complete. Total published: {total_published} movies."
    )
    return total_published


@shared_task(name="movie.app.tasks.embedding_tasks.sync_movie_embeddings")
def sync_movie_embeddings(
    batch_size: int = EMBEDDING_BATCH_SIZE,
    max_items: Optional[int] = None,
):
    """
    Celery task: publishes all movies with descriptions to RabbitMQ so the
    recommendations service can generate and store embedding vectors.

    This is useful for:
    - Initial bulk population of movie_embeddings table
    - Re-syncing after a data migration
    - One-off manual trigger via Celery CLI

    Usage:
        celery -A movie.app.tasks.celery_app call movie.app.tasks.embedding_tasks.sync_movie_embeddings
        celery -A movie.app.tasks.celery_app call movie.app.tasks.embedding_tasks.sync_movie_embeddings --kwargs '{"max_items": 100}'
    """
    logger.info(
        f"Starting embedding sync pipeline "
        f"(batch_size={batch_size}, max_items={max_items})..."
    )
    try:
        total = asyncio.run(
            run_sync_embeddings_pipeline(
                batch_size=batch_size,
                max_items=max_items,
            )
        )
        msg = f"Embedding sync completed. Published {total} movies to recommendations."
        logger.info(msg)
        return msg
    except Exception as e:
        logger.exception("Error during embedding sync pipeline")
        raise e
