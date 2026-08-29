from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


Role = Literal["admin", "support", "user"]


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, examples=["Carlos Herrera"])
    email: EmailStr = Field(..., examples=["carlos@example.com"])
    role: Role = Field(..., examples=["user"])
    is_active: bool = Field(default=True, examples=[True])


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

