import asyncio
import logging
import random
from typing import Optional, List, Tuple, cast
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from recomendations.config import config
from recomendations.app.repository.sql import recommendation_repository as recommendation_db
from recomendations.models import MovieEmbeddingModel

logger = logging.getLogger(__name__)


from recomendations.exception.exceptions import NotFound
from recomendations.app.repository.cache.recommendation_redis_repository import RecommendationRedisRepository
from recomendations.app.schemas.recommendation import MovieListItemSchema


class RecommendationService:
    def __init__(self, session: AsyncSession, cache: Optional[RecommendationRedisRepository] = None):
        self.session = session
        self.cache = cache

    def _get_model(self):
        from recomendations.core import embedder
        if embedder.model is None:
            from sentence_transformers import SentenceTransformer
            embedder.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        assert embedder.model is not None
        return embedder.model

    def _get_text_to_encode(self, title: str, description: str, release_year: Optional[int], genres: Optional[str]) -> str:
        genres_list = genres.split(", ") if genres else []
        genres_str = ", ".join(genres_list) if genres_list else "нет"
        year_str = str(release_year) if release_year else "неизвестно"
        return f"Фильм: {title} ({year_str}). Жанры: {genres_str}. Описание: {description}"

    async def upsert_movie_embedding(self, movie_id: int, movie_data: dict) -> None:
        title = movie_data.get("title") or ""
        original_title = movie_data.get("original_title")
        description = movie_data.get("description") or ""
        release_year = movie_data.get("release_year")
        poster_url = movie_data.get("poster_url")
        genres_list = movie_data.get("genres") or []
        imdb_id = movie_data.get("imdb_id")
        imdb_rating = movie_data.get("imdb_rating")

        genres_str = ", ".join(genres_list) if genres_list else None

        description_vector = None
        if description and description.strip():
            try:
                model = self._get_model()
                text_to_encode = self._get_text_to_encode(
                    title=title,
                    description=description,
                    release_year=release_year,
                    genres=genres_str
                )
                embedding = await asyncio.to_thread(model.encode, text_to_encode)
                description_vector = cast(List[float], embedding.tolist() if hasattr(embedding, "tolist") else embedding)
            except Exception as e:
                logger.error(f"Failed to compute embedding for movie {movie_id}: {e}")
                description_vector = None

        await recommendation_db.upsert(
            session=self.session,
            movie_id=movie_id,
            title=title,
            description=description,
            release_year=release_year,
            poster_url=poster_url,
            genres=genres_str,
            description_vector=description_vector,
            imdb_rating=imdb_rating,
        )
        await self.session.commit()

    async def delete_movie_embedding(self, movie_id: int) -> None:
        await recommendation_db.delete_embedding(self.session, movie_id)
        await self.session.commit()

    async def get_similar_movies(
        self,
        movie_id: int,
        limit: int = 20
    ) -> List[MovieListItemSchema]:
        if self.cache:
            try:
                cached = await self.cache.get_similar_movies(movie_id)
                if cached:
                    logger.info(f"Cache hit for similar movies of movie_id: {movie_id}")
                    return cached
            except Exception as e:
                logger.error(f"Failed to read from similar movies cache: {e}")

        target_movie = await recommendation_db.get_by_id(self.session, movie_id)
        if not target_movie:
            random_films = await recommendation_db.get_random_films(self.session, limit=limit)
            return await self.fetch_movie_items_via_rest([m.movie_id for m in random_films])

        description = target_movie.description
        if not description or not description.strip():
            random_films = await recommendation_db.get_random_films(self.session, limit=limit)
            return await self.fetch_movie_items_via_rest([m.movie_id for m in random_films])

        target_vector = target_movie.description_vector

        if target_vector is None:
            try:
                model = self._get_model()
                text_to_encode = self._get_text_to_encode(
                    title=target_movie.title,
                    description=description,
                    release_year=target_movie.release_year,
                    genres=target_movie.genres
                )
                embedding = await asyncio.to_thread(model.encode, text_to_encode)
                target_vector = cast(List[float], embedding.tolist() if hasattr(embedding, "tolist") else embedding)

                target_movie.description_vector = target_vector
                await self.session.commit()
            except Exception as e:
                logger.error(f"Failed to generate embedding on the fly for movie {movie_id}: {e}")
                raise e

        db_items = await recommendation_db.get_similar_movies(
            session=self.session,
            movie_id=movie_id,
            target_vector=target_vector,
            limit=limit,
        )

        similar_ids = [m.movie_id for m in db_items]
        items = await self.fetch_movie_items_via_rest(similar_ids)

        if self.cache:
            try:
                ttl = 86400 if (target_movie.imdb_rating is not None and target_movie.imdb_rating >= 7.5) else 3600
                await self.cache.save_similar_movies(movie_id, items, ttl=ttl)
                logger.info(f"Cached similar movies for movie_id: {movie_id} with TTL {ttl}s")
            except Exception as e:
                logger.error(f"Failed to cache similar movies: {e}")

        return items

    async def generate_embeddings_batch(self, limit: int = 50) -> bool:
        movies = await recommendation_db.get_unencoded(self.session, limit=limit)
        if not movies:
            return False

        try:
            model = self._get_model()
            texts_to_encode = []
            for m in movies:
                desc = m.description or ""
                text = self._get_text_to_encode(
                    title=m.title,
                    description=desc,
                    release_year=m.release_year,
                    genres=m.genres
                )
                texts_to_encode.append(text)

            embeddings = await asyncio.to_thread(model.encode, texts_to_encode, batch_size=32)

            for movie, emb in zip(movies, embeddings):
                movie.description_vector = cast(List[float], emb.tolist() if hasattr(emb, "tolist") else emb)

            await self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error in embedding generation batch: {e}")
            raise e

    async def get_custom_recommendations(
        self,
        movie_ids: List[int],
        genres: List[str],
        release_year: Optional[int],
        release_year_from: Optional[int] = None,
        release_year_to: Optional[int] = None,
        imdb_rating_from: Optional[float] = None,
        media_type: Optional[str] = None,
        custom_description: Optional[str] = None,
        limit: int = 20
    ) -> List[MovieListItemSchema]:
        vectors = []
        if movie_ids:
            movies = await recommendation_db.get_by_ids(self.session, movie_ids)
            for m in movies:
                if m.description_vector is not None:
                    vectors.append(m.description_vector)

        if custom_description and custom_description.strip():
            try:
                model = self._get_model()
                text_to_encode = custom_description.strip()
                logger.info(f"ENCODING CUSTOM DESCRIPTION WITH MODEL: {model}")
                embedding = await asyncio.to_thread(model.encode, text_to_encode)
                custom_vector = cast(List[float], embedding.tolist() if hasattr(embedding, "tolist") else embedding)
                vectors.append(custom_vector)
            except Exception as e:
                logger.error(f"Failed to compute embedding for custom description: {e}")

        if not vectors:
            return []

        avg_vector = [sum(col) / len(vectors) for col in zip(*vectors)]

        db_items = await recommendation_db.get_similar_movies_custom(
            session=self.session,
            target_vector=avg_vector,
            exclude_ids=movie_ids,
            genres=genres,
            release_year=release_year,
            release_year_from=release_year_from,
            release_year_to=release_year_to,
            imdb_rating_from=imdb_rating_from,
            media_type=media_type,
            limit=limit
        )

        similar_ids = [m.movie_id for m in db_items]
        results = await self.fetch_movie_items_via_rest(similar_ids)

        if len(results) < limit:
            fallback_items = await self.fetch_custom_fallback_from_movie_service(
                genres=genres,
                release_year_from=release_year_from,
                release_year_to=release_year_to,
                imdb_rating_from=imdb_rating_from,
                media_type=media_type,
                exclude_ids=movie_ids + [item.id for item in results],
                limit=limit - len(results),
            )
            results.extend(fallback_items)

        return results

    async def fetch_custom_fallback_from_movie_service(
        self,
        genres: List[str],
        release_year_from: Optional[int] = None,
        release_year_to: Optional[int] = None,
        imdb_rating_from: Optional[float] = None,
        media_type: Optional[str] = None,
        exclude_ids: Optional[List[int]] = None,
        limit: int = 12,
    ) -> List[MovieListItemSchema]:
        page = random.randint(1, 4)
        params: dict = {"limit": limit * 2, "page": page, "sort_by": "random"}
        if genres:
            params["genre_name"] = genres[0]
        if release_year_from:
            params["year_from"] = release_year_from
        if release_year_to:
            params["year_to"] = release_year_to
        if imdb_rating_from:
            params["imdb_rating_from"] = imdb_rating_from
        if media_type:
            params["media_type"] = media_type

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{config.MOVIE_SERVICE_URL}/api/v1/movies",
                    params=params,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    raw_items = data.get("items", [])
                    exclude_set = set(exclude_ids or [])
                    filtered = [
                        MovieListItemSchema.model_validate(item)
                        for item in raw_items
                        if item["id"] not in exclude_set
                    ]
                    random.shuffle(filtered)
                    return filtered[:limit]
        except Exception as e:
            logger.error(f"Fallback fetch error from movie service: {e}")

        return []

    async def fetch_movie_items_via_rest(self, movie_ids: List[int]) -> List[MovieListItemSchema]:
        if not movie_ids:
            return []

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{config.MOVIE_SERVICE_URL}/api/v1/movies/batch",
                    json={"movie_ids": movie_ids},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    items_map = {item["id"]: MovieListItemSchema.model_validate(item) for item in data}
                    return [items_map[mid] for mid in movie_ids if mid in items_map]
                else:
                    logger.error(f"Failed to fetch movies from movie service: status={resp.status_code}")
        except Exception as e:
            logger.error(f"HTTP error fetching movies from movie service: {e}")

        db_movies = await recommendation_db.get_by_ids(self.session, movie_ids)
        movies_map = {m.movie_id: m for m in db_movies}
        fallback_items = []
        for mid in movie_ids:
            m = movies_map.get(mid)
            if m:
                fallback_items.append(
                    MovieListItemSchema(
                        id=m.movie_id,
                        title=m.title,
                        original_title=m.original_title,
                        release_year=m.release_year,
                        poster_url=m.poster_url,
                        genres=m.genres.split(", ") if m.genres else [],
                        imdb_id=m.imdb_id,
                        imdb_rating=m.imdb_rating,
                        imdb_votes=m.imdb_votes,
                        tmdb_id=m.tmdb_id,
                        tmdb_rating=m.tmdb_rating,
                        tmdb_votes=m.tmdb_votes,
                        media_type=m.media_type,
                    )
                )
        return fallback_items
