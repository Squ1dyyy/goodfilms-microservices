from celery import shared_task
import asyncio
import logging
from typing import Dict, List, Optional
import requests
import tmdbsimple as tmdb
from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType
from sqlalchemy import select, update, bindparam, func, text

from movie.config import config
from movie.database.context import AsyncSessionLocal
from movie.models.items import MoviesModel, MediaTypesModel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

tmdb.API_KEY = config.TMDB_API_KEY
RPS_LIMIT = 20
BATCH_SIZE = 20

MEDIA_TYPE_MAP = {
    "movie": 1,
    "tv": 2,
    "tv_episode": 3,
    "tv_season": 4,
}


def fetch_media_by_imdb(imdb_id: str) -> Optional[Dict]:
    """Получает информацию о фильме или сериале из TMDb по IMDb ID строго за 1 запрос."""
    try:
        find = tmdb.Find(imdb_id)
        data = find.info(external_source="imdb_id", language="ru-RU")

        item = None
        media_type = None

        if data.get("movie_results"):
            item = data["movie_results"][0]
            media_type = item.get("media_type") or "movie"
        elif data.get("tv_results"):
            item = data["tv_results"][0]
            media_type = item.get("media_type") or "tv"
        elif data.get("tv_episode_results"):
            item = data["tv_episode_results"][0]
            media_type = item.get("media_type") or "tv_episode"
        elif data.get("tv_season_results"):
            item = data["tv_season_results"][0]
            media_type = item.get("media_type") or "tv_season"

        if item:
            poster = item.get("poster_path")
            backdrop = item.get("backdrop_path")
            title = (
                item.get("title")
                or item.get("name")
                or item.get("original_title")
                or item.get("original_name")
            )
            original_title = (
                item.get("original_title")
                or item.get("original_name")
                or item.get("title")
                or item.get("name")
            )
            release_date = item.get("release_date") or item.get("first_air_date")
            is_adult = item.get("adult", False)

            overview = item.get("overview")
            description = overview if overview and overview.strip() else None

            media_type_id = MEDIA_TYPE_MAP.get(media_type, 1)

            return {
                "tmdb_id": item.get("id"),
                "imdb_id": imdb_id,
                "media_type": media_type,
                "media_type_id": media_type_id,
                "title": title,
                "original_title": original_title,
                "release_date": release_date,
                "tmdb_rating": round(item.get("vote_average"), 2) if item.get("vote_average") is not None else None,
                "tmdb_votes": item.get("vote_count"),
                "is_adult": is_adult,
                "description": description,
                "poster_url": poster,
                "backdrop_url": backdrop,
            }
        else:
            logging.warning(f"Контент с IMDb ID {imdb_id} не найден на TMDb.")
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            logging.warning(
                f"[429 Rate Limit] Превышен лимит на ID {imdb_id}. Ждем..."
            )
        else:
            logging.error(f"HTTP ошибка для IMDb ID {imdb_id}: {e}")
    except Exception as e:
        logging.error(f"Исключение при запросе {imdb_id}: {e}")

    return None


class GlobalRateLimiter:
    """Гарантирует, что глобальная частота вызовов к TMDb API строго не превышает rps_limit."""
    def __init__(self, rps_limit: float = RPS_LIMIT):
        self.interval = 1.0 / rps_limit
        self.lock = asyncio.Lock()
        self.last_call = 0.0

    async def acquire(self):
        async with self.lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self.last_call
            if elapsed < self.interval:
                await asyncio.sleep(self.interval - elapsed)
            self.last_call = asyncio.get_event_loop().time()


async def worker(queue: asyncio.Queue, results: list, not_found_ids: list, rate_limiter: GlobalRateLimiter):
    """Воркер, забирающий задачи из очереди с соблюдением глобального RPS_LIMIT."""
    while not queue.empty():
        imdb_id = await queue.get()

        await rate_limiter.acquire()
        media = await asyncio.to_thread(fetch_media_by_imdb, imdb_id)

        if media:
            results.append(media)
            logger.info(
                f"[TMDb Found] {media['media_type'].upper()} (ID: {media['media_type_id']}) '{media['title']}' "
                f"(IMDb: {media['imdb_id']}, TMDb ID: {media['tmdb_id']}, Rating: {media['tmdb_rating']})"
            )
        else:
            not_found_ids.append(imdb_id)
            logger.warning(f"[TMDb Not Found] Контент с IMDb ID {imdb_id} не найден на TMDb.")

        queue.task_done()


async def fetch_imdb_ids_from_db(
    batch_size: int = BATCH_SIZE,
    offset: int = 0,
    only_missing: bool = True,
) -> List[str]:
    """Извлекает IMDb ID из БД, отсортированные по популярности (imdb_votes DESC)."""
    async with AsyncSessionLocal() as session:
        stmt = select(MoviesModel.imdb_id).where(MoviesModel.imdb_id.is_not(None))

        if only_missing:
            stmt = stmt.where(MoviesModel.is_tmdb_checked.is_(False))

        stmt = (
            stmt.order_by(
                MoviesModel.imdb_votes.desc().nulls_last(),
                MoviesModel.id.asc(),
            )
            .offset(offset)
            .limit(batch_size)
        )

        result = await session.execute(stmt)
        return [row[0] for row in result.all()]


async def mark_movies_as_tmdb_checked(imdb_ids: List[str]):
    """Помечает список IMDb ID как проверенные в TMDb, чтобы повторно не запрашивать их."""
    if not imdb_ids:
        return

    async with AsyncSessionLocal() as session:
        async with session.begin():
            table = MoviesModel.__table__
            stmt = (
                update(table)
                .where(table.c.imdb_id.in_(imdb_ids))
                .values(is_tmdb_checked=True)
            )
            await session.execute(stmt)
            logger.info(f"Помечено как проверенные (но не найденные) в TMDb: {len(imdb_ids)} записей.")


async def update_movies_batch_in_db(updates: List[Dict]):
    """Пакетное обновление TMDb данных в PostgreSQL с использованием внешнего ключа media_type_id."""
    if not updates:
        return

    seen_tmdb_ids = set()
    for m in updates:
        tid = m.get("tmdb_id")
        if tid is not None:
            if tid in seen_tmdb_ids:
                logger.warning(
                    f"Дублирующий tmdb_id {tid} найден внутри одного батча для {m['imdb_id']}. Сбрасываем tmdb_id."
                )
                m["tmdb_id"] = None
            else:
                seen_tmdb_ids.add(tid)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            tmdb_ids = [m["tmdb_id"] for m in updates if m.get("tmdb_id") is not None]
            if tmdb_ids:
                existing_stmt = select(MoviesModel.imdb_id, MoviesModel.tmdb_id).where(
                    MoviesModel.tmdb_id.in_(tmdb_ids)
                )
                existing_res = await session.execute(existing_stmt)
                existing_map = {row[1]: row[0] for row in existing_res.all()}

                for m in updates:
                    tid = m.get("tmdb_id")
                    if tid and tid in existing_map and existing_map[tid] != m["imdb_id"]:
                        logger.warning(
                            f"tmdb_id {tid} для IMDb {m['imdb_id']} уже занят фильмом IMDb {existing_map[tid]} в БД. Пропускаем обновление tmdb_id."
                        )
                        m["tmdb_id"] = None

            table = MoviesModel.__table__
            stmt = (
                update(table)
                .where(table.c.imdb_id == bindparam("b_imdb_id"))
                .values(
                    title=func.coalesce(bindparam("b_title"), table.c.title),
                    original_title=func.coalesce(bindparam("b_original_title"), table.c.original_title),
                    tmdb_id=bindparam("b_tmdb_id"),
                    tmdb_rating=bindparam("b_tmdb_rating"),
                    tmdb_votes=bindparam("b_tmdb_votes"),
                    media_type_id=bindparam("b_media_type_id"),
                    is_adult=bindparam("b_is_adult"),
                    description=func.coalesce(func.nullif(table.c.description, ""), bindparam("b_description")),
                    poster_url=func.coalesce(table.c.poster_url, bindparam("b_poster_url")),
                    backdrop_url=func.coalesce(table.c.backdrop_url, bindparam("b_backdrop_url")),
                    is_tmdb_checked=True,
                )
            )

            params = [
                {
                    "b_imdb_id": m["imdb_id"],
                    "b_title": m["title"],
                    "b_original_title": m["original_title"],
                    "b_tmdb_id": m["tmdb_id"],
                    "b_tmdb_rating": m["tmdb_rating"],
                    "b_tmdb_votes": m["tmdb_votes"],
                    "b_media_type_id": m["media_type_id"],
                    "b_is_adult": m["is_adult"],
                    "b_description": m["description"],
                    "b_poster_url": m["poster_url"],
                    "b_backdrop_url": m["backdrop_url"],
                }
                for m in updates
            ]

            try:
                await session.execute(stmt, params)
                logger.info(f"Успешно обновлено в базе данных {len(updates)} записей.")
            except Exception as e:
                logger.warning(f"Ошибка при пакетном обновлении: {e}. Выполняем поштучное обновление...")
                for p in params:
                    try:
                        async with session.begin_nested():
                            await session.execute(stmt, [p])
                    except Exception as item_err:
                        logger.error(f"Не удалось обновить запись IMDb {p['b_imdb_id']}: {item_err}")



_films_exchange = RabbitExchange(name="films", type=ExchangeType.TOPIC)


async def publish_batch_to_recommendations(movies: List[Dict]) -> None:
    """Publish a batch of TMDB-synced movies to RabbitMQ for embedding generation.
    Only publishes movies that have a description.
    """
    movies_with_desc = [m for m in movies if m.get("description")]
    if not movies_with_desc:
        logger.info("No movies with descriptions in batch; skipping RabbitMQ publish.")
        return

    broker = RabbitBroker(config.RABBIT_BROKER_URL)
    async with broker:
        await broker.declare_exchange(_films_exchange)
        for movie in movies_with_desc:
            try:
                await broker.publish(
                    message={
                        "movie_id": movie["tmdb_id"],
                        "title": movie["title"] or "",
                        "description": movie.get("description"),
                        "release_year": _parse_release_year(movie.get("release_date")),
                        "poster_url": movie.get("poster_url"),
                        "genres": [],
                        "imdb_rating": movie.get("tmdb_rating"),
                    },
                    exchange=_films_exchange,
                    routing_key="movie.updated",
                )
            except Exception as e:
                logger.error(
                    f"Failed to publish embedding event for '{movie.get('title')}': {e}"
                )
    logger.info(
        f"Published {len(movies_with_desc)} movie events to recommendations service."
    )


async def publish_batch_to_recommendations_with_ids(
    movies: List[Dict], db_ids: List[int]
) -> None:
    """Publish movies to RabbitMQ using their actual DB IDs from movie_db.
    Matches by imdb_id position since update_movies_batch_in_db processes them in order.
    """
    movies_with_desc = [m for m in movies if m.get("description")]
    if not movies_with_desc:
        logger.info("No movies with descriptions in batch; skipping RabbitMQ publish.")
        return

    broker = RabbitBroker(config.RABBIT_BROKER_URL)
    async with broker:
        await broker.declare_exchange(_films_exchange)
        for movie, db_id in zip(movies_with_desc, db_ids):
            try:
                await broker.publish(
                    message={
                        "movie_id": db_id,
                        "title": movie["title"] or "",
                        "description": movie.get("description"),
                        "release_year": _parse_release_year(movie.get("release_date")),
                        "poster_url": movie.get("poster_url"),
                        "genres": [],
                        "imdb_rating": movie.get("tmdb_rating"),
                    },
                    exchange=_films_exchange,
                    routing_key="movie.updated",
                )
            except Exception as e:
                logger.error(
                    f"Failed to publish embedding event for '{movie.get('title')}': {e}"
                )
    logger.info(
        f"Published {len(movies_with_desc)} movie events with DB IDs to recommendations."
    )


def _parse_release_year(release_date: Optional[str]) -> Optional[int]:
    """Extract year from a date string like '2023-05-12'."""
    if not release_date:
        return None
    try:
        return int(str(release_date)[:4])
    except (ValueError, TypeError):
        return None


async def clean_existing_full_urls_in_db():
    """Удаляет префикс полного URL (https://image.tmdb.org/t/p/...) из БД, оставляя только относительные ключи путей."""
    async with AsyncSessionLocal() as session:
        has_full_urls = await session.scalar(
            select(func.count(MoviesModel.id)).where(MoviesModel.poster_url.like("https://image.tmdb.org/t/p/%"))
        )
        if not has_full_urls:
            return

        async with session.begin():
            await session.execute(
                text("""
                    UPDATE movies
                    SET poster_url = REGEXP_REPLACE(poster_url, '^https://image\\.tmdb\\.org/t/p/[^/]+', '')
                    WHERE poster_url LIKE 'https://image.tmdb.org/t/p/%';
                """)
            )
            await session.execute(
                text("""
                    UPDATE movies
                    SET backdrop_url = REGEXP_REPLACE(backdrop_url, '^https://image\\.tmdb\\.org/t/p/[^/]+', '')
                    WHERE backdrop_url LIKE 'https://image.tmdb.org/t/p/%';
                """)
            )
            logger.info("Полные URL постеров и кадров в БД очищены до относительных ключей TMDb.")


async def process_tmdb_sync_pipeline(
    batch_size: int = BATCH_SIZE,
    max_items: Optional[int] = None,
    only_missing: bool = True,
) -> int:
    """Главный конвейер синхронизации TMDb данных батчами по 20 записей."""
    await clean_existing_full_urls_in_db()

    total_processed = 0
    offset = 0

    while True:
        current_batch_size = batch_size
        if max_items is not None:
            remaining = max_items - total_processed
            if remaining <= 0:
                break
            current_batch_size = min(batch_size, remaining)

        imdb_ids = await fetch_imdb_ids_from_db(
            batch_size=current_batch_size,
            offset=offset if not only_missing else 0,
            only_missing=only_missing,
        )

        if not imdb_ids:
            logger.info("Нет фильмов для обработки TMDb.")
            break

        logger.info(f"Обработка батча из {len(imdb_ids)} медиафайлов (IMDb votes DESC)...")

        queue = asyncio.Queue()
        for imdb_id in imdb_ids:
            queue.put_nowait(imdb_id)

        rate_limiter = GlobalRateLimiter(rps_limit=RPS_LIMIT)
        results = []
        not_found_ids = []
        workers = [
            asyncio.create_task(worker(queue, results, not_found_ids, rate_limiter))
            for _ in range(8)
        ]

        await queue.join()
        for w in workers:
            w.cancel()

        if results:
            await update_movies_batch_in_db(results)
            total_processed += len(results)

            try:
                db_ids = await _fetch_db_ids_for_batch(results)
                await publish_batch_to_recommendations_with_ids(results, db_ids)
            except Exception as e:
                logger.error(
                    f"Failed to publish batch to recommendations service: {e}"
                )

        if not_found_ids:
            await mark_movies_as_tmdb_checked(not_found_ids)

        if not only_missing:
            offset += len(imdb_ids)

        if len(imdb_ids) < current_batch_size:
            break

    logger.info(f"TMDb sync завершен. Успешно обновлено в БД: {total_processed} записей.")
    return total_processed


async def _fetch_db_ids_for_batch(movies: List[Dict]) -> List[int]:
    """Fetch actual DB IDs for a batch of movies by their imdb_id.
    Returns IDs in the same order as movies (only for movies with descriptions).
    """
    movies_with_desc = [m for m in movies if m.get("description")]
    if not movies_with_desc:
        return []

    imdb_ids = [m["imdb_id"] for m in movies_with_desc]
    async with AsyncSessionLocal() as session:
        from movie.models.items import MoviesModel
        stmt = select(MoviesModel.id, MoviesModel.imdb_id).where(
            MoviesModel.imdb_id.in_(imdb_ids)
        )
        result = await session.execute(stmt)
        id_map = {row[1]: row[0] for row in result.all()}

    return [id_map[m["imdb_id"]] for m in movies_with_desc if m["imdb_id"] in id_map]


@shared_task(name="movie.app.tasks.tmdb_tasks.run_tmdb_sync")
def run_tmdb_sync(
    batch_size: int = 20,
    max_items: Optional[int] = None,
    only_missing: bool = True,
):
    logger.info(f"Starting TMDb sync pipeline (batch_size={batch_size}, max_items={max_items})...")

    try:
        processed_count = asyncio.run(
            process_tmdb_sync_pipeline(
                batch_size=batch_size,
                max_items=max_items,
                only_missing=only_missing,
            )
        )
        return f"TMDb sync completed successfully. Processed {processed_count} items."
    except Exception as e:
        logger.exception("Error during TMDb sync pipeline execution")
        raise e


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Синхронизация данных фильмов/сериалов из TMDb.")
    parser.add_argument(
        "-c", "--count", "--limit",
        type=int,
        default=None,
        help="Количество записей для спарсенных за данный запуск (например: -c 50). По умолчанию: все незаполненные.",
    )
    parser.add_argument(
        "-b", "--batch-size",
        type=int,
        default=20,
        help="Размер батча (по умолчанию: 20).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Принудительно перепроверить все фильмы, даже если поля TMDb уже заполнены.",
    )

    args = parser.parse_args()
    run_tmdb_sync(
        batch_size=args.batch_size,
        max_items=args.count,
        only_missing=not args.all,
    )
