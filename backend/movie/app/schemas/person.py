from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

from movie.app.schemas.base import PaginatedResponseSchema
from movie.app.schemas.movie import MovieListItemSchema


class PersonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    birth_date: Optional[date] = None
    photo_url: Optional[str] = None


class PersonMoviesSchema(BaseModel):
    person: PersonSchema
    movies: PaginatedResponseSchema[MovieListItemSchema]


class CreatePersonSchema(BaseModel):
    full_name: str
    birth_date: Optional[date] = None
    photo_url: Optional[str] = None


class UpdatePersonSchema(BaseModel):
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    photo_url: Optional[str] = None


class PersonQueryParams(BaseModel):
    search: Optional[str] = None
