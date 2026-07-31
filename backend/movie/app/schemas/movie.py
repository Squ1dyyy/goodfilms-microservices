from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict, field_validator

T = TypeVar("T")


class PaginationSchema(BaseModel):
    limit: int = Field(20, ge=1, le=50)
    page: int = Field(1, ge=1)


class BatchMoviesRequest(BaseModel):
    movie_ids: list[int]


class PaginatedResponseSchema(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int


class MediaListItemSchema(BaseModel):                         
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    original_title: Optional[str] = None
    release_year: Optional[int] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    media_type: Optional[str] = None
    is_adult: bool = False
    genres: list[str]
    imdb_id: Optional[str] = None
    imdb_rating: Optional[float] = None
    imdb_votes: Optional[int] = None
    tmdb_id: Optional[int] = None
    tmdb_rating: Optional[float] = None
    tmdb_votes: Optional[int] = None
    trailer_url: Optional[str] = None

    @field_validator("genres", mode="before")
    @classmethod
    def extract_genre_names(cls, value):
        return [g.name if hasattr(g, "name") else g for g in value]


class PersonInMediaSchema(BaseModel):                                   
    person_id: int
    full_name: str
    photo_url: Optional[str]
    character_name: Optional[str]
    billing_order: Optional[int]


class MediaDetailSchema(BaseModel):
    id: int
    title: str
    original_title: Optional[str] = None
    description: str
    release_year: Optional[int] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    media_type: Optional[str] = None
    is_adult: bool = False
    imdb_id: Optional[str] = None
    imdb_rating: Optional[float] = None
    imdb_votes: Optional[int] = None
    tmdb_id: Optional[int] = None
    tmdb_rating: Optional[float] = None
    tmdb_votes: Optional[int] = None
    trailer_url: Optional[str] = None

    genres: list[str]
    studios: list[str]
    keywords: list[str] = Field(default_factory=list)

    cast: list[PersonInMediaSchema]
    directors: list[PersonInMediaSchema]
    writers: list[PersonInMediaSchema]
    producers: list[PersonInMediaSchema]


class MediaQueryParams(BaseModel):
    genre_id: Optional[int] = None
    genre_name: Optional[str] = None
    media_type: Optional[str] = None
    is_adult: Optional[bool] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    imdb_rating_from: Optional[float] = None
    imdb_rating_to: Optional[float] = None
    imdb_votes_from: Optional[int] = None
    tmdb_rating_from: Optional[float] = None
    tmdb_rating_to: Optional[float] = None
    tmdb_votes_from: Optional[int] = None
    search: Optional[str] = None
    sort_by: Optional[str] = None


class CreateMediaSchema(BaseModel):
    title: str
    original_title: Optional[str] = None
    release_year: Optional[int] = None
    runtime_minutes: Optional[int] = None
    description: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    media_type: Optional[str] = None
    is_adult: bool = False
    imdb_id: Optional[str] = None
    imdb_rating: Optional[float] = None
    imdb_votes: Optional[int] = None
    tmdb_id: Optional[int] = None
    tmdb_rating: Optional[float] = None
    tmdb_votes: Optional[int] = None
    trailer_url: Optional[str] = None
    genre_ids: list[int] = Field(default_factory=list)
    studio_ids: list[int] = Field(default_factory=list)
    country_ids: list[int] = Field(default_factory=list)
    keyword_ids: list[int] = Field(default_factory=list)


class UpdateMediaSchema(BaseModel):
    title: Optional[str] = None
    original_title: Optional[str] = None
    release_year: Optional[int] = None
    runtime_minutes: Optional[int] = None
    description: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    media_type: Optional[str] = None
    is_adult: Optional[bool] = None
    imdb_id: Optional[str] = None
    imdb_rating: Optional[float] = None
    imdb_votes: Optional[int] = None
    tmdb_id: Optional[int] = None
    tmdb_rating: Optional[float] = None
    tmdb_votes: Optional[int] = None
    trailer_url: Optional[str] = None
    genre_ids: Optional[list[int]] = None
    studio_ids: Optional[list[int]] = None
    country_ids: Optional[list[int]] = None
    keyword_ids: Optional[list[int]] = None


MovieListItemSchema = MediaListItemSchema
PersonInMovieSchema = PersonInMediaSchema
MovieDetailSchema = MediaDetailSchema
MovieQueryParams = MediaQueryParams
CreateMovieSchema = CreateMediaSchema
UpdateMovieSchema = UpdateMediaSchema


class AddMoviePersonSchema(BaseModel):
    person_id: int
    profession_id: int
    character_name: Optional[str] = None
    billing_order: Optional[int] = None


class UpdateMoviePersonSchema(BaseModel):
    profession_id: Optional[int] = None
    character_name: Optional[str] = None
    billing_order: Optional[int] = None
