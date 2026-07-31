from typing import Optional
from sqlalchemy import Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from monorepo.shared.db.base import Base


class MovieEmbeddingModel(Base):
    __tablename__ = "movie_embeddings"

    movie_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    original_title: Mapped[Optional[str]] = mapped_column(String(255))
    release_year: Mapped[Optional[int]] = mapped_column(Integer)
    poster_url: Mapped[Optional[str]] = mapped_column(String(500))
    genres: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    description_vector: Mapped[Optional[list[float]]] = mapped_column(Vector(384))
    imdb_id: Mapped[Optional[str]] = mapped_column(String(20))
    imdb_rating: Mapped[Optional[float]] = mapped_column(Float)
    imdb_votes: Mapped[Optional[int]] = mapped_column(Integer)
    tmdb_id: Mapped[Optional[int]] = mapped_column(Integer)
    tmdb_rating: Mapped[Optional[float]] = mapped_column(Float)
    tmdb_votes: Mapped[Optional[int]] = mapped_column(Integer)
    media_type: Mapped[Optional[str]] = mapped_column(String(50))

    def __str__(self) -> str:
        return f"{self.title} ({self.release_year})"
