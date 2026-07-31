"""add username to reviews

Revision ID: 92b90d7d9d5f
Revises: 81a80c6c8c4e
Create Date: 2026-06-29 21:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "92b90d7d9d5f"
down_revision: Union[str, Sequence[str], None] = "81a80c6c8c4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "reviews", sa.Column("username", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("reviews", "username")
