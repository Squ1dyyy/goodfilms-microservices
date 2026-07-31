"""Initial migration

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-06-22 15:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "genres",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "studios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "persons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "professions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "movies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("original_title", sa.String(length=255), nullable=True),
        sa.Column("release_year", sa.Integer(), nullable=True),
        sa.Column("runtime_minutes", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("poster_url", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "movie_countries",
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"]),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"]),
        sa.PrimaryKeyConstraint("movie_id", "country_id"),
    )
    op.create_table(
        "movie_genres",
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["genre_id"], ["genres.id"]),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"]),
        sa.PrimaryKeyConstraint("movie_id", "genre_id"),
    )
    op.create_table(
        "movie_studios",
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("studio_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"]),
        sa.ForeignKeyConstraint(["studio_id"], ["studios.id"]),
        sa.PrimaryKeyConstraint("movie_id", "studio_id"),
    )
    op.create_table(
        "movie_persons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.Column("profession_id", sa.Integer(), nullable=False),
        sa.Column("character_name", sa.String(length=255), nullable=True),
        sa.Column("billing_order", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"]),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"]),
        sa.ForeignKeyConstraint(["profession_id"], ["professions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("movie_persons")
    op.drop_table("movie_studios")
    op.drop_table("movie_genres")
    op.drop_table("movie_countries")
    op.drop_table("movies")
    op.drop_table("professions")
    op.drop_table("persons")
    op.drop_table("studios")
    op.drop_table("genres")
    op.drop_table("countries")
