"""Initial migration

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-07-21 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "movie_embeddings",
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("release_year", sa.Integer(), nullable=True),
        sa.Column("poster_url", sa.String(length=500), nullable=True),
        sa.Column("genres", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("description_vector", Vector(dim=384), nullable=True),
        sa.Column("imdb_rating", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("movie_id"),
    )


def downgrade() -> None:
    op.drop_table("movie_embeddings")
