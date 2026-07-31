from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator, AliasChoices
from recomendations.app.schemas.base import PaginatedResponseSchema


class PaginationSchema(BaseModel):
    limit: int = Field(20, ge=1, le=100)
    page: int = Field(1, ge=1)


class MovieListItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(validation_alias=AliasChoices("id", "movie_id"))
    title: str
    original_title: Optional[str] = None
    release_year: Optional[int] = None
    poster_url: Optional[str] = None
    genres: list[str] = []
    imdb_id: Optional[str] = None
    imdb_rating: Optional[float] = None
    imdb_votes: Optional[int] = None
    tmdb_id: Optional[int] = None
    tmdb_rating: Optional[float] = None
    tmdb_votes: Optional[int] = None
    media_type: Optional[str] = None

    @field_validator("genres", mode="before")
    @classmethod
    def parse_genres(cls, v):
        if isinstance(v, str):
            return [g.strip() for g in v.split(",") if g.strip()]
        return v or []


class PaginatedSimilarResponse(PaginatedResponseSchema[MovieListItemSchema]):
    pass


class MovieCreatedEventSchema(BaseModel):
    movie_id: int
    title: str
    original_title: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None
    poster_url: Optional[str] = None
    genres: List[str] = []
    imdb_id: Optional[str] = None
    imdb_rating: Optional[float] = None
    imdb_votes: Optional[int] = None
    tmdb_id: Optional[int] = None
    tmdb_rating: Optional[float] = None
    tmdb_votes: Optional[int] = None
    media_type: Optional[str] = None


class MovieDeletedEventSchema(BaseModel):
    movie_id: int


class CustomRecommendationRequest(BaseModel):
    movie_ids: List[int] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    release_year: Optional[int] = None
    release_year_from: Optional[int] = None
    release_year_to: Optional[int] = None
    imdb_rating_from: Optional[float] = None
    media_type: Optional[str] = None
    custom_description: Optional[str] = None
    limit: Optional[int] = Field(12, ge=1, le=50)
