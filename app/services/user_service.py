from typing import Any

from fastapi import HTTPException, status

from app.data.users_db import users_db
from app.schemas.user_schema import Role, UserCreate, UserUpdate, UserUpdatePartial


class UserService:
    @staticmethod
    def get_all_users(role: Role | None = None, is_active: bool | None = None) -> list[dict]:
        filtered_users = users_db.copy()

        if role is not None:
            filtered_users = [user for user in filtered_users if user["role"] == role]

        if is_active is not None:
            filtered_users = [user for user in filtered_users if user["is_active"] == is_active]

        return filtered_users

    @staticmethod
    def get_user_by_id(user_id: int) -> dict:
        user = next((user for user in users_db if user["id"] == user_id), None)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        return user

    @staticmethod
    def email_exists(email: str) -> bool:
        return any(user["email"].lower() == email.lower() for user in users_db)

    @staticmethod
    def create_user(user_data: UserCreate) -> dict:
        if UserService.email_exists(str(user_data.email)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correo electrónico duplicado",
            )

        new_user = {
            "id": len(users_db) + 1,
            "name": user_data.name,
            "email": str(user_data.email),
            "role": user_data.role,
            "is_active": user_data.is_active,
        }
        users_db.append(new_user)
        return new_user

    @staticmethod
    def update_user_full(user_id: int, user_data: UserUpdate) -> dict:
        user = UserService.get_user_by_id(user_id)

        if user["email"].lower() != str(user_data.email).lower() and UserService.email_exists(str(user_data.email)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correo electrónico duplicado",
            )

        user.update(
            {
                "name": user_data.name,
                "email": str(user_data.email),
                "role": user_data.role,
                "is_active": user_data.is_active,
            }
        )
        return user

    @staticmethod
    def update_user_partial(user_id: int, user_data: UserUpdatePartial) -> dict:
        user = UserService.get_user_by_id(user_id)

        if not user_data.model_dump(exclude_unset=True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe enviar al menos un campo para actualizar",
            )

        updated_data = user_data.model_dump(exclude_unset=True)

        if "email" in updated_data:
            email = str(updated_data["email"])
            if user["email"].lower() != email.lower() and UserService.email_exists(email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Correo electrónico duplicado",
                )

        user.update(updated_data)
        return user

    @staticmethod
    def delete_user(user_id: int) -> None:
        user = UserService.get_user_by_id(user_id)
        users_db.remove(user)
