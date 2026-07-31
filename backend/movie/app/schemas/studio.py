from pydantic import BaseModel, ConfigDict


class StudioSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CreateStudioSchema(BaseModel):
    name: str


class UpdateStudioSchema(BaseModel):
    name: str
