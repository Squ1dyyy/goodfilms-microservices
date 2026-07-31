from pydantic import BaseModel, ConfigDict


class ProfessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CreateProfessionSchema(BaseModel):
    name: str


class UpdateProfessionSchema(BaseModel):
    name: str
