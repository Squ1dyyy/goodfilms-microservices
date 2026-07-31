"""add ratings

Revision ID: 81a80c6c8c4e
Revises: 70f79b5b7b3d
Create Date: 2026-06-29 21:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "81a80c6c8c4e"
down_revision: Union[str, Sequence[str], None] = "70f79b5b7b3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reviews_ratings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("movie_id", "user_id", name="uq_movie_user_rating"),
    )
    op.create_index(
        op.f("ix_reviews_ratings_movie_id"),
        "reviews_ratings",
        ["movie_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reviews_ratings_user_id"), "reviews_ratings", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reviews_ratings_user_id"), table_name="reviews_ratings")
    op.drop_index(op.f("ix_reviews_ratings_movie_id"), table_name="reviews_ratings")
    op.drop_table("reviews_ratings")
