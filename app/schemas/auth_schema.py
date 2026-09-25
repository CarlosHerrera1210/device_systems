from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


AuthRole = Literal["admin", "support", "user"]


class UserRegister(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, examples=["Ana Perez"])
    email: EmailStr = Field(..., examples=["ana@example.com"])
    password: str = Field(..., min_length=8, max_length=72, examples=["SecurePass1"])
    role: AuthRole = Field(default="user", examples=["user"])
    is_active: bool = Field(default=True, examples=[True])

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar 72 bytes")
        if any(character.isspace() for character in value):
            raise ValueError("La contraseña no puede contener espacios")
        if not any(character.isupper() for character in value):
            raise ValueError("La contraseña debe contener una mayúscula")
        if not any(character.islower() for character in value):
            raise ValueError("La contraseña debe contener una minúscula")
        if not any(character.isdigit() for character in value):
            raise ValueError("La contraseña debe contener un número")
        return value

    @field_validator("role")
    @classmethod
    def validate_public_role(cls, value: AuthRole) -> AuthRole:
        if value == "admin":
            raise ValueError("El rol admin debe asignarse mediante un proceso administrativo")
        return value

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
    role: AuthRole


class AuthUserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: AuthRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
