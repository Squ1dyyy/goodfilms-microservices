from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from auth.app.schemas.user import UserPublicSchema


class SessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    country: Optional[str] = None

    @field_validator("ip_address", mode="before")
    @classmethod
    def coerce_ip_to_str(cls, value):
        return str(value) if value is not None else None


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    user: UserPublicSchema


class AccessTokenSchema(BaseModel):
    access_token: str
