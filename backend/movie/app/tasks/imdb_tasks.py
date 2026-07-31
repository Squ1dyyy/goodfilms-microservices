import asyncio
import csv
import gzip
import logging
import os
import shutil
import tempfile
import requests
from celery import shared_task
from sqlalchemy import text
from movie.database.context import engine

logger = logging.getLogger(__name__)

IMDB_DATASETS = {
    "basics": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "ratings": "https://datasets.imdbws.com/title.ratings.tsv.gz",
    "akas": "https://datasets.imdbws.com/title.akas.tsv.gz",
    "crew": "https://datasets.imdbws.com/title.crew.tsv.gz",
    "principals": "https://datasets.imdbws.com/title.principals.tsv.gz",
    "names": "https://datasets.imdbws.com/name.basics.tsv.gz",
}

async def import_basics_to_db(filepath: str):
    logger.info("Starting basics dataset import...")
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TEMP TABLE IF NOT EXISTS staging_movies (
                    imdb_id VARCHAR(20) PRIMARY KEY,
                    title VARCHAR(255),
                    original_title VARCHAR(255),
                    release_year INT,
                    runtime_minutes INT,
                    genres_list TEXT
                ) ON COMMIT DROP;
            """))
            
            raw_conn = await conn.get_raw_connection()
            asyncpg_conn = raw_conn.driver_connection
            if asyncpg_conn is None and hasattr(raw_conn, "dbapi_connection"):
                dbapi_conn = raw_conn.dbapi_connection
                asyncpg_conn = getattr(dbapi_conn, "driver_connection", None) or getattr(dbapi_conn, "dbapi_connection", None)
            if asyncpg_conn is None:
                raise RuntimeError(
                    f"Could not extract asyncpg connection from {type(raw_conn)}. "
                    f"Attributes: {dir(raw_conn)}"
                )
            
            batch = []
            batch_size = 50000
            count = 0
            
            with gzip.open(filepath, mode="rt", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                for row in reader:
                    if row.get("titleType") not in ("movie", "tvSeries", "tvMiniSeries", "tvSpecial", "tvMovie"):
                        continue
                    
                    imdb_id = row.get("tconst")
                    title = row.get("primaryTitle")
                    if title:
                        title = title[:255]
                    original_title = row.get("originalTitle")
                    if original_title:
                        original_title = original_title[:255]
                    
                    release_year_str = row.get("startYear")
                    release_year = int(release_year_str) if release_year_str and release_year_str != "\\N" else None
                    
                    runtime_str = row.get("runtimeMinutes")
                    runtime_minutes = int(runtime_str) if runtime_str and runtime_str != "\\N" else None
                    
                    genres_list = row.get("genres")
                    if genres_list == "\\N":
                        genres_list = None
                    
                    batch.append((imdb_id, title, original_title, release_year, runtime_minutes, genres_list))
                    
                    if len(batch) >= batch_size:
                        await asyncpg_conn.copy_records_to_table(
                            "staging_movies",
                            records=batch,
                            columns=["imdb_id", "title", "original_title", "release_year", "runtime_minutes", "genres_list"]
                        )
                        count += len(batch)
                        logger.info(f"Copied {count} records into basics staging table...")
                        batch = []
                        
                if batch:
                    await asyncpg_conn.copy_records_to_table(
                        "staging_movies",
                        records=batch,
                        columns=["imdb_id", "title", "original_title", "release_year", "runtime_minutes", "genres_list"]
                    )
                    count += len(batch)
                    logger.info(f"Copied final {len(batch)} records (total {count}) into basics staging table...")
            
            logger.info("Merging staging table into main 'movies' table...")
            await conn.execute(text("""
                INSERT INTO movies (imdb_id, title, original_title, release_year, runtime_minutes)
                SELECT imdb_id, title, original_title, release_year, runtime_minutes
                FROM staging_movies
                ON CONFLICT (imdb_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    original_title = EXCLUDED.original_title,
                    release_year = EXCLUDED.release_year,
                    runtime_minutes = EXCLUDED.runtime_minutes;
            """))
            
            logger.info("Extracting and inserting unique genres...")
            await conn.execute(text("""
                INSERT INTO genres (name)
                SELECT DISTINCT unnest(string_to_array(genres_list, ','))
                FROM staging_movies
                WHERE genres_list IS NOT NULL
                ON CONFLICT (name) DO NOTHING;
            """))
            
            logger.info("Linking genres to movies...")
            await conn.execute(text("""
                INSERT INTO movie_genres (movie_id, genre_id)
                SELECT m.id, g.id
                FROM staging_movies sm
                JOIN movies m ON m.imdb_id = sm.imdb_id
                JOIN genres g ON g.name = ANY(string_to_array(sm.genres_list, ','))
                ON CONFLICT DO NOTHING;
            """))
            
            logger.info("Basics dataset import complete.")
    finally:
        await engine.dispose()



async def import_ratings_to_db(filepath: str):
    logger.info("Starting ratings dataset import...")
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TEMP TABLE IF NOT EXISTS staging_ratings (
                    imdb_id VARCHAR(20) PRIMARY KEY,
                    imdb_rating FLOAT,
                    imdb_votes INT
                ) ON COMMIT DROP;
            """))
            
            raw_conn = await conn.get_raw_connection()
            asyncpg_conn = raw_conn.driver_connection
            if asyncpg_conn is None and hasattr(raw_conn, "dbapi_connection"):
                dbapi_conn = raw_conn.dbapi_connection
                asyncpg_conn = getattr(dbapi_conn, "driver_connection", None) or getattr(dbapi_conn, "dbapi_connection", None)
            if asyncpg_conn is None:
                raise RuntimeError(
                    f"Could not extract asyncpg connection from {type(raw_conn)}. "
                    f"Attributes: {dir(raw_conn)}"
                )
            
            batch = []
            batch_size = 50000
            count = 0
            
            with gzip.open(filepath, mode="rt", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                for row in reader:
                    imdb_id = row.get("tconst")
                    
                    rating_str = row.get("averageRating")
                    imdb_rating = float(rating_str) if rating_str and rating_str != "\\N" else None
                    
                    votes_str = row.get("numVotes")
                    imdb_votes = int(votes_str) if votes_str and votes_str != "\\N" else None
                    
                    batch.append((imdb_id, imdb_rating, imdb_votes))
                    
                    if len(batch) >= batch_size:
                        await asyncpg_conn.copy_records_to_table(
                            "staging_ratings",
                            records=batch,
                            columns=["imdb_id", "imdb_rating", "imdb_votes"]
                        )
                        count += len(batch)
                        logger.info(f"Copied {count} records into ratings staging table...")
                        batch = []
                        
                if batch:
                    await asyncpg_conn.copy_records_to_table(
                        "staging_ratings",
                        records=batch,
                        columns=["imdb_id", "imdb_rating", "imdb_votes"]
                    )
                    count += len(batch)
                    logger.info(f"Copied final {len(batch)} records (total {count}) into ratings staging table...")
            
            logger.info("Updating ratings in 'movies' table from staging...")
            await conn.execute(text("""
                UPDATE movies m
                SET imdb_rating = r.imdb_rating,
                    imdb_votes = r.imdb_votes
                FROM staging_ratings r
                WHERE m.imdb_id = r.imdb_id;
            """))
            logger.info("Ratings dataset import complete.")
    finally:
        await engine.dispose()


async def import_akas_to_db(filepath: str):
    logger.info("Starting AKAs (localized titles) import...")
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT id, imdb_id FROM movies WHERE imdb_id IS NOT NULL"))
            movie_map = {row[1]: row[0] for row in result.fetchall()}
            
            ru_titles = {}
            
            with gzip.open(filepath, mode="rt", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                for row in reader:
                    title_id = row.get("titleId")
                    if title_id not in movie_map:
                        continue
                    
                    region = row.get("region")
                    lang = row.get("language")
                    is_ru = region == "RU" or lang == "ru"
                    
                    if is_ru:
                        title = row.get("title")
                        if title:
                            is_original = row.get("isOriginalTitle") == "1"
                            if title_id not in ru_titles or not is_original:
                                ru_titles[title_id] = title
            
            logger.info(f"Found {len(ru_titles)} Russian titles. Updating database...")
            
            batch = []
            for imdb_id, new_title in ru_titles.items():
                batch.append({"imdb_id": imdb_id, "title": new_title[:255]})
                if len(batch) >= 20000:
                    await conn.execute(
                        text("UPDATE movies SET title = :title WHERE imdb_id = :imdb_id"),
                        batch
                    )
                    batch = []
            if batch:
                await conn.execute(
                    text("UPDATE movies SET title = :title WHERE imdb_id = :imdb_id"),
                    batch
                )
            
            logger.info("AKAs import complete.")
    finally:
        await engine.dispose()


async def import_cast_crew_to_db(crew_path: str, principals_path: str, names_path: str):
    logger.info("Starting cast and crew import...")
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
                INSERT INTO professions (id, name) VALUES
                (1, 'cast'),
                (2, 'directors'),
                (3, 'writers'),
                (4, 'producers')
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
            """))
            
            result = await conn.execute(text("SELECT id, imdb_id FROM movies WHERE imdb_id IS NOT NULL"))
            movie_map = {row[1]: row[0] for row in result.fetchall()}
            
            await conn.execute(text("""
                CREATE TEMP TABLE IF NOT EXISTS staging_movie_persons (
                    movie_imdb_id VARCHAR(20),
                    person_imdb_id VARCHAR(20),
                    category VARCHAR(50),
                    character_name VARCHAR(255),
                    billing_order INT
                ) ON COMMIT DROP;
            """))
            
            await conn.execute(text("""
                CREATE TEMP TABLE IF NOT EXISTS staging_persons (
                    person_imdb_id VARCHAR(20) PRIMARY KEY,
                    full_name VARCHAR(255),
                    birth_year INT
                ) ON COMMIT DROP;
            """))
            
            raw_conn = await conn.get_raw_connection()
            asyncpg_conn = raw_conn.driver_connection
            if asyncpg_conn is None and hasattr(raw_conn, "dbapi_connection"):
                dbapi_conn = raw_conn.dbapi_connection
                asyncpg_conn = getattr(dbapi_conn, "driver_connection", None) or getattr(dbapi_conn, "dbapi_connection", None)
            if asyncpg_conn is None:
                raise RuntimeError("Could not extract asyncpg connection.")
            
            active_person_ids = set()
            
            logger.info("Parsing title.crew...")
            batch = []
            with gzip.open(crew_path, mode="rt", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                for row in reader:
                    tconst = row.get("tconst")
                    if tconst not in movie_map:
                        continue
                    
                    directors = row.get("directors")
                    writers = row.get("writers")
                    
                    if directors and directors != "\\N":
                        for d in directors.split(","):
                            active_person_ids.add(d)
                            batch.append((tconst, d, "directors", None, None))
                    if writers and writers != "\\N":
                        for w in writers.split(","):
                            active_person_ids.add(w)
                            batch.append((tconst, w, "writers", None, None))
                            
                    if len(batch) >= 50000:
                        await asyncpg_conn.copy_records_to_table(
                            "staging_movie_persons",
                            records=batch,
                            columns=["movie_imdb_id", "person_imdb_id", "category", "character_name", "billing_order"]
                        )
                        batch = []
            if batch:
                await asyncpg_conn.copy_records_to_table(
                    "staging_movie_persons",
                    records=batch,
                    columns=["movie_imdb_id", "person_imdb_id", "category", "character_name", "billing_order"]
                )
            
            logger.info("Parsing title.principals...")
            batch = []
            with gzip.open(principals_path, mode="rt", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                for row in reader:
                    tconst = row.get("tconst")
                    if tconst not in movie_map:
                        continue
                    
                    category = row.get("category")
                    if category in ("actor", "actress", "self"):
                        norm_category = "cast"
                    elif category == "director":
                        norm_category = "directors"
                    elif category == "writer":
                        norm_category = "writers"
                    elif category == "producer":
                        norm_category = "producers"
                    else:
                        continue
                    
                    nconst = row.get("nconst")
                    active_person_ids.add(nconst)
                    
                    billing_order_str = row.get("ordering")
                    billing_order = int(billing_order_str) if billing_order_str and billing_order_str != "\\N" else None
                    
                    char_name = row.get("characters")
                    if char_name and char_name != "\\N":
                        if char_name.startswith("[") and char_name.endswith("]"):
                            import json
                            try:
                                chars = json.loads(char_name)
                                if isinstance(chars, list) and chars:
                                    char_name = ", ".join(chars)
                            except Exception:
                                char_name = char_name.strip("[]\"'")
                        char_name = char_name[:255]
                    else:
                        char_name = None
                        
                    batch.append((tconst, nconst, norm_category, char_name, billing_order))
                    
                    if len(batch) >= 50000:
                        await asyncpg_conn.copy_records_to_table(
                            "staging_movie_persons",
                            records=batch,
                            columns=["movie_imdb_id", "person_imdb_id", "category", "character_name", "billing_order"]
                        )
                        batch = []
            if batch:
                await asyncpg_conn.copy_records_to_table(
                    "staging_movie_persons",
                    records=batch,
                    columns=["movie_imdb_id", "person_imdb_id", "category", "character_name", "billing_order"]
                )
                
            logger.info(f"Identified {len(active_person_ids)} active cast/crew members.")
            
            logger.info("Parsing name.basics...")
            batch = []
            with gzip.open(names_path, mode="rt", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                for row in reader:
                    nconst = row.get("nconst")
                    if nconst not in active_person_ids:
                        continue
                    
                    full_name = row.get("primaryName")
                    if full_name:
                        full_name = full_name[:255]
                        
                    birth_year_str = row.get("birthYear")
                    birth_year = int(birth_year_str) if birth_year_str and birth_year_str != "\\N" else None
                    
                    batch.append((nconst, full_name, birth_year))
                    
                    if len(batch) >= 50000:
                        await asyncpg_conn.copy_records_to_table(
                            "staging_persons",
                            records=batch,
                            columns=["person_imdb_id", "full_name", "birth_year"]
                        )
                        batch = []
            if batch:
                await asyncpg_conn.copy_records_to_table(
                    "staging_persons",
                    records=batch,
                    columns=["person_imdb_id", "full_name", "birth_year"]
                )
                
            logger.info("Merging staging_persons into persons table...")
            await conn.execute(text("""
                INSERT INTO persons (id, full_name, birth_date)
                SELECT DISTINCT
                    CAST(SUBSTRING(person_imdb_id FROM 3) AS INT),
                    full_name,
                    CASE 
                        WHEN birth_year IS NOT NULL AND birth_year > 0 THEN MAKE_DATE(birth_year, 1, 1) 
                        ELSE NULL 
                    END
                FROM staging_persons
                ON CONFLICT (id) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    birth_date = EXCLUDED.birth_date;
            """))
            
            logger.info("Clearing old movie_persons relationships...")
            await conn.execute(text("DELETE FROM movie_persons"))
            
            logger.info("Merging staging_movie_persons into movie_persons table...")
            await conn.execute(text("""
                INSERT INTO movie_persons (movie_id, person_id, profession_id, character_name, billing_order)
                SELECT DISTINCT
                    m.id,
                    pers.id,
                    p.id,
                    smp.character_name,
                    smp.billing_order
                FROM staging_movie_persons smp
                JOIN movies m ON m.imdb_id = smp.movie_imdb_id
                JOIN professions p ON p.name = smp.category
                JOIN persons pers ON pers.id = CAST(SUBSTRING(smp.person_imdb_id FROM 3) AS INT)
                ON CONFLICT DO NOTHING;
            """))
            
            logger.info("Cast and crew import complete.")
    finally:
        await engine.dispose()


def download_file(url: str, dest: str):
    logger.info(f"Downloading {url} to {dest}...")
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()
    with open(dest, "wb") as f:
        shutil.copyfileobj(response.raw, f)
    logger.info(f"Download complete: {dest}")


@shared_task(name="movie.app.tasks.imdb_tasks.run_imdb_sync")
def run_imdb_sync():
    logger.info("Starting IMDb sync pipeline...")
    
    temp_dir = tempfile.gettempdir()
    basics_path = os.path.join(temp_dir, "title.basics.tsv.gz")
    ratings_path = os.path.join(temp_dir, "title.ratings.tsv.gz")
    akas_path = os.path.join(temp_dir, "title.akas.tsv.gz")
    crew_path = os.path.join(temp_dir, "title.crew.tsv.gz")
    principals_path = os.path.join(temp_dir, "title.principals.tsv.gz")
    names_path = os.path.join(temp_dir, "name.basics.tsv.gz")
    
    all_paths = (basics_path, ratings_path, akas_path, crew_path, principals_path, names_path)
    
    try:
        download_file(IMDB_DATASETS["basics"], basics_path)
        asyncio.run(import_basics_to_db(basics_path))
        
        download_file(IMDB_DATASETS["ratings"], ratings_path)
        asyncio.run(import_ratings_to_db(ratings_path))
        
        download_file(IMDB_DATASETS["akas"], akas_path)
        asyncio.run(import_akas_to_db(akas_path))
        
        download_file(IMDB_DATASETS["crew"], crew_path)
        download_file(IMDB_DATASETS["principals"], principals_path)
        download_file(IMDB_DATASETS["names"], names_path)
        asyncio.run(import_cast_crew_to_db(crew_path, principals_path, names_path))
        
        logger.info("IMDb sync pipeline completed successfully.")
        return "IMDb sync completed successfully"
    except Exception as e:
        logger.exception("Error during IMDb sync pipeline execution")
        raise e
    finally:
        for path in all_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(f"Cleaned up temporary file: {path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {path}: {e}")
