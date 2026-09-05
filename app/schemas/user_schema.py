from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


Role = Literal["admin", "support", "user"]


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, examples=["Carlos Herrera"])
    email: EmailStr = Field(..., examples=["carlos@example.com"])
    role: Role = Field(..., examples=["user"])
    is_active: bool = Field(default=True, examples=[True])


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=3, examples=["Carlos Herrera"])
    email: EmailStr = Field(..., examples=["carlos@example.com"])
    role: Role = Field(..., examples=["admin"])
    is_active: bool = Field(..., examples=[True])


class UserUpdatePartial(BaseModel):
    name: str | None = Field(default=None, min_length=3, examples=["Carlos Herrera"])
    email: EmailStr | None = Field(default=None, examples=["carlos@example.com"])
    role: Role | None = Field(default=None, examples=["support"])
    is_active: bool | None = Field(default=None, examples=[True])


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class APIMessage(BaseModel):
    message: str


class UserListResponse(BaseModel):
    total: int
    users: list[UserResponse]


class ErrorResponse(BaseModel):
    error: bool
    message: str
    status_code: int

