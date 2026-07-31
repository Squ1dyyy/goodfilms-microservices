"""add media_types table and media_type_id column

Revision ID: e7f8a9b0c1d2
Revises: d6f7e8a9b0c1
Create Date: 2026-07-28 22:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e7f8a9b0c1d2'
down_revision: Union[str, Sequence[str], None] = 'd6f7e8a9b0c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'media_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.execute("INSERT INTO media_types (id, name) VALUES (1, 'movie'), (2, 'tv'), (3, 'tv_episode'), (4, 'tv_season') ON CONFLICT DO NOTHING;")

    op.add_column('movies', sa.Column('media_type_id', sa.Integer(), server_default='1', nullable=True))
    op.create_foreign_key(None, 'movies', 'media_types', ['media_type_id'], ['id'])

    try:
        op.drop_column('movies', 'media_type')
    except Exception:
        pass


def downgrade() -> None:
    op.add_column('movies', sa.Column('media_type', sa.String(length=20), nullable=True))
    op.drop_constraint(None, 'movies', type_='foreignkey')
    op.drop_column('movies', 'media_type_id')
    op.drop_table('media_types')
