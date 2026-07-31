from pydantic import BaseModel
from typing import Optional


class MovieEventSchema(BaseModel):
    movie_id: int
    title: str
    description: Optional[str] = None
    release_year: Optional[int] = None
    poster_url: Optional[str] = None
    genres: list[str] = []
    imdb_rating: Optional[float] = None


class MovieDeletedEventSchema(BaseModel):
    movie_id: int


class PersonEventSchema(BaseModel):
    person_id: int
    full_name: str


class PersonDeletedEventSchema(BaseModel):
    person_id: int


class MoviePersonAddedEventSchema(BaseModel):
    movie_id: int
    person_id: int
    profession_id: int


class MoviePersonRemovedEventSchema(BaseModel):
    movie_id: int
    person_id: int
