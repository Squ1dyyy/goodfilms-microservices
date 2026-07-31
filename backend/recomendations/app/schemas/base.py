from pydantic import BaseModel
from typing_extensions import Generic, TypeVar

T = TypeVar("T")


class PaginatedResponseSchema(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
