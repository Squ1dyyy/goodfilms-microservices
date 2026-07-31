import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    ForeignKey,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import mapped_column, Mapped, relationship
from reviews.models.base import Base


class ReviewsModel(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movie_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    review: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    reactions: Mapped[List["ReviewsReactionsModel"]] = relationship(
        "ReviewsReactionsModel", back_populates="review", cascade="all, delete-orphan"
    )
    comments: Mapped[List["ReviewsCommentsModel"]] = relationship(
        "ReviewsCommentsModel", back_populates="review", cascade="all, delete-orphan"
    )


class ReviewsReactionsModel(Base):
    __tablename__ = "reviews_reactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    reaction: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    review_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False
    )
    review: Mapped["ReviewsModel"] = relationship(
        "ReviewsModel", back_populates="reactions"
    )


class ReviewsCommentsModel(Base):
    __tablename__ = "reviews_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    review_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False
    )
    review: Mapped["ReviewsModel"] = relationship(
        "ReviewsModel", back_populates="comments"
    )


class ReviewsRatingsModel(Base):
    __tablename__ = "reviews_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movie_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("movie_id", "user_id", name="uq_movie_user_rating"),
    )
