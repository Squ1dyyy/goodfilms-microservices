from pydantic import BaseModel, ConfigDict


class GenreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CreateGenreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class UpdateGenreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
