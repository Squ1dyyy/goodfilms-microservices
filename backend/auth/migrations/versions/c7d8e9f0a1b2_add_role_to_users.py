"""Add role to users

Revision ID: c7d8e9f0a1b2
Revises: a1b2c3d4e5f6
Create Date: 2026-06-23 22:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7d8e9f0a1b2"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=50),
            nullable=False,
            server_default="user",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
