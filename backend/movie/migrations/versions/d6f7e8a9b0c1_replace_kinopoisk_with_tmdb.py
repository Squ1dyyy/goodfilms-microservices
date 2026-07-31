"""replace kinopoisk with tmdb and add media fields

Revision ID: d6f7e8a9b0c1
Revises: c5e31a980753
Create Date: 2026-07-28 21:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd6f7e8a9b0c1'
down_revision: Union[str, Sequence[str], None] = 'c5e31a980753'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('movies_kinopoisk_id_key', 'movies', type_='unique')
    op.drop_column('movies', 'kinopoisk_votes')
    op.drop_column('movies', 'kinopoisk_rating')
    op.drop_column('movies', 'kinopoisk_id')

    op.add_column('movies', sa.Column('backdrop_url', sa.String(length=500), nullable=True))
    op.add_column('movies', sa.Column('media_type', sa.String(length=20), server_default='movie', nullable=True))
    op.add_column('movies', sa.Column('is_adult', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('movies', sa.Column('tmdb_id', sa.Integer(), nullable=True))
    op.add_column('movies', sa.Column('tmdb_rating', sa.Float(), nullable=True))
    op.add_column('movies', sa.Column('tmdb_votes', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'movies', ['tmdb_id'])


def downgrade() -> None:
    op.drop_constraint(None, 'movies', type_='unique')
    op.drop_column('movies', 'tmdb_votes')
    op.drop_column('movies', 'tmdb_rating')
    op.drop_column('movies', 'tmdb_id')
    op.drop_column('movies', 'is_adult')
    op.drop_column('movies', 'media_type')
    op.drop_column('movies', 'backdrop_url')

    op.add_column('movies', sa.Column('kinopoisk_id', sa.Integer(), nullable=True))
    op.add_column('movies', sa.Column('kinopoisk_rating', sa.Float(), nullable=True))
    op.add_column('movies', sa.Column('kinopoisk_votes', sa.Integer(), nullable=True))
    op.create_unique_constraint('movies_kinopoisk_id_key', 'movies', ['kinopoisk_id'])
