from datetime import timedelta
from celery import Celery
from movie.config import config

celery_app = Celery(
    "movie_tasks",
    broker=config.RABBIT_BROKER_URL,
    backend=config.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "sync-imdb-daily": {
        "task": "movie.app.tasks.imdb_tasks.run_imdb_sync",
        "schedule": timedelta(days=1),
    },
    "sync-tmdb-daily": {
        "task": "movie.app.tasks.tmdb_tasks.run_tmdb_sync",
        "schedule": timedelta(days=1),
        "kwargs": {"only_missing": False},
    },
    "sync-embeddings-weekly": {
        "task": "movie.app.tasks.embedding_tasks.sync_movie_embeddings",
        "schedule": timedelta(weeks=1),
    },
}

celery_app.conf.imports = (
    "movie.app.tasks.imdb_tasks",
    "movie.app.tasks.tmdb_tasks",
    "movie.app.tasks.embedding_tasks",
)
