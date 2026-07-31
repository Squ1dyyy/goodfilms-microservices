"""add description vector column

Revision ID: c5e31a980753
Revises: 85490ff03785
Create Date: 2026-07-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = 'c5e31a980753'
down_revision: Union[str, Sequence[str], None] = '85490ff03785'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column('movies', sa.Column('description_vector', Vector(dim=384), nullable=True))


def downgrade() -> None:
    op.drop_column('movies', 'description_vector')
