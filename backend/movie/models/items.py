from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from movie.models.base import Base


movie_countries = Table(
    "movie_countries",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("country_id", ForeignKey("countries.id"), primary_key=True),
)

movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)

movie_studios = Table(
    "movie_studios",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("studio_id", ForeignKey("studios.id"), primary_key=True),
)

movie_keywords = Table(
    "movie_keywords",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("keyword_id", ForeignKey("keywords.id"), primary_key=True),
)


class MediaTypesModel(Base):
    __tablename__ = "media_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    movies: Mapped[list["MoviesModel"]] = relationship(back_populates="media_type_rel")

    def __str__(self) -> str:
        return self.name


class MoviesModel(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    original_title: Mapped[Optional[str]] = mapped_column(String(255))
    release_year: Mapped[Optional[int]] = mapped_column(Integer)
    runtime_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)
    poster_url: Mapped[Optional[str]] = mapped_column(String(500))
    backdrop_url: Mapped[Optional[str]] = mapped_column(String(500))
    media_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("media_types.id"), nullable=True)
    is_adult: Mapped[bool] = mapped_column(Boolean, default=False)
    imdb_id: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    imdb_rating: Mapped[Optional[float]] = mapped_column(Float)
    imdb_votes: Mapped[Optional[int]] = mapped_column(Integer)
    tmdb_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True)
    tmdb_rating: Mapped[Optional[float]] = mapped_column(Float)
    tmdb_votes: Mapped[Optional[int]] = mapped_column(Integer)
    is_tmdb_checked: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    trailer_url: Mapped[Optional[str]] = mapped_column(String(500))

    media_type_rel: Mapped[Optional["MediaTypesModel"]] = relationship(back_populates="movies")

    @property
    def media_type(self) -> Optional[str]:
        if "media_type_rel" in self.__dict__:
            return self.media_type_rel.name if self.media_type_rel else None
        return None

    countries: Mapped[list["CountriesModel"]] = relationship(
        secondary=movie_countries, back_populates="movies"
    )
    genres: Mapped[list["GenresModel"]] = relationship(
        secondary=movie_genres, back_populates="movies"
    )
    studios: Mapped[list["StudiosModel"]] = relationship(
        secondary=movie_studios, back_populates="movies"
    )
    keywords: Mapped[list["KeywordsModel"]] = relationship(
        secondary=movie_keywords, back_populates="movies"
    )

    movie_persons: Mapped[list["MoviePersonsModel"]] = relationship(
        back_populates="movie"
    )

    def __str__(self) -> str:
        return f"{self.title} ({self.release_year})"


class CountriesModel(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    movies: Mapped[list["MoviesModel"]] = relationship(
        secondary=movie_countries, back_populates="countries"
    )

    def __str__(self) -> str:
        return self.name


class GenresModel(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    movies: Mapped[list["MoviesModel"]] = relationship(
        secondary=movie_genres, back_populates="genres"
    )

    def __str__(self) -> str:
        return self.name


class StudiosModel(Base):
    __tablename__ = "studios"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    movies: Mapped[list["MoviesModel"]] = relationship(
        secondary=movie_studios, back_populates="studios"
    )

    def __str__(self) -> str:
        return self.name


class KeywordsModel(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    movies: Mapped[list["MoviesModel"]] = relationship(
        secondary=movie_keywords, back_populates="keywords"
    )

    def __str__(self) -> str:
        return self.name


class PersonsModel(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))

    movie_persons: Mapped[list["MoviePersonsModel"]] = relationship(
        back_populates="person"
    )

    def __str__(self) -> str:
        return self.full_name


class ProfessionsModel(Base):
    __tablename__ = "professions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    movie_persons: Mapped[list["MoviePersonsModel"]] = relationship(
        back_populates="profession"
    )

    def __str__(self) -> str:
        return self.name


class MoviePersonsModel(Base):
    __tablename__ = "movie_persons"

    id: Mapped[int] = mapped_column(primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    profession_id: Mapped[int] = mapped_column(ForeignKey("professions.id"))
    character_name: Mapped[Optional[str]] = mapped_column(String(255))
    billing_order: Mapped[Optional[int]] = mapped_column(Integer)

    movie: Mapped["MoviesModel"] = relationship(back_populates="movie_persons")
    person: Mapped["PersonsModel"] = relationship(back_populates="movie_persons")
    profession: Mapped["ProfessionsModel"] = relationship(
        back_populates="movie_persons"
    )

    def __str__(self) -> str:
        movie_obj = self.__dict__.get("movie")
        movie_str = movie_obj.title if movie_obj else f"Movie #{self.movie_id}"

        person_obj = self.__dict__.get("person")
        person_str = person_obj.full_name if person_obj else f"Person #{self.person_id}"

        prof_obj = self.__dict__.get("profession")
        prof_str = prof_obj.name if prof_obj else f"Profession #{self.profession_id}"

        char_info = f" as {self.character_name}" if self.character_name else ""
        return f"{person_str} ({prof_str}{char_info}) in {movie_str}"
