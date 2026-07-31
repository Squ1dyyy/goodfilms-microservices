from pydantic import BaseModel, ConfigDict


class CountrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CreateCountrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class UpdateCountrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
