from fastapi import Depends, Header, HTTPException, status

from app.data.users_db import users_db
from app.schemas.user_schema import Role


def get_user_or_404(user_id: int):
    user = next((user for user in users_db if user["id"] == user_id), None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return user


def validate_email_not_exists(email: str) -> str:
    if any(user["email"].lower() == email.lower() for user in users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correo electrónico duplicado",
        )
    return email


def validate_role(role: Role | None = None) -> Role | None:
    if role is not None and role not in ["admin", "support", "user"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Rol no permitido",
        )
    return role


def get_api_config() -> dict:
    return {
        "app_name": "device_systems",
        "version": "2.0.0",
        "environment": "development",
    }


def get_current_user_agent(user_agent: str | None = Header(default=None, alias="User-Agent")) -> str | None:
    if user_agent is None:
        return None
    return user_agent
