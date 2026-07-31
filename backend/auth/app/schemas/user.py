from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str


class RegisterUserSchema(BaseModel):
    email: EmailStr
    username: str
    password: str
    password_confirm: str


class UserDataSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    role: str


class UserPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: Optional[EmailStr] = None
    is_verified: bool = False


class EditPasswordSchema(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str


class EmailSchema(BaseModel):
    email: EmailStr


class NewPasswordSchema(BaseModel):
    new_password: str


class TokenSchema(BaseModel):
    token: str


class AdminUpdateUserSchema(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None


T = TypeVar("T")


class PaginationSchema(BaseModel):
    limit: int = Field(20, ge=1, le=50)
    page: int = Field(1, ge=1)


class PaginatedResponseSchema(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
