import asyncio
import os
import sys
from logging.config import fileConfig

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from movie.models.base import Base
from movie.models.items import (
    MoviesModel,
    CountriesModel,
    GenresModel,
    StudiosModel,
    PersonsModel,
    ProfessionsModel,
    MoviePersonsModel,
)
from movie.config import config as app_config

alembic_config = context.config
alembic_config.set_main_option("sqlalchemy.url", app_config.DATABASE_URL)

if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
