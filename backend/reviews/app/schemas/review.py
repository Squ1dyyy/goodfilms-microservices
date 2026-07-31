from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class PaginationSchema(BaseModel):
    limit: int = Field(20, ge=1, le=50)
    last_id: Optional[int] = Field(None, ge=1)


class PaginatedResponseSchema(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: Optional[int] = None
    limit: int


class ReviewCreateSchema(BaseModel):
    review: str = Field(min_length=0, max_length=5000)
    username: Optional[str] = None


class ReviewResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    movie_id: int
    user_id: int
    username: Optional[str] = None
    review: str = Field(min_length=0, max_length=5000)


class RatingCreateSchema(BaseModel):
    rating: int = Field(ge=1, le=10)
    movie_id: int


class RatingSummarySchema(BaseModel):
    average_rating: float
    total_ratings: int
    distribution: dict[int, int]
