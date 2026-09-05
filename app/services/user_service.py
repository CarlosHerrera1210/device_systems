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
    def create_user(user_data: UserCreate) -> dict:
        if any(u["email"].lower() == str(user_data.email).lower() for u in users_db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correo electrónico duplicado",
            )

        new_id = max((u["id"] for u in users_db), default=0) + 1
        new_user = {
            "id": new_id,
            "name": user_data.name,
            "email": str(user_data.email),
            "role": user_data.role,
            "is_active": user_data.is_active,
        }
        users_db.append(new_user)
        return new_user

    @staticmethod
    def update_user_full(user: dict, user_data: UserUpdate) -> dict:
        if user["email"].lower() != str(user_data.email).lower():
            if any(u["email"].lower() == str(user_data.email).lower() for u in users_db):
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
    def update_user_partial(user: dict, user_data: UserUpdatePartial) -> dict:
        updated_data = user_data.model_dump(exclude_unset=True)

        if not updated_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe enviar al menos un campo para actualizar",
            )

        if "email" in updated_data:
            email = str(updated_data["email"])
            if user["email"].lower() != email.lower():
                if any(u["email"].lower() == email.lower() for u in users_db):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Correo electrónico duplicado",
                    )

        user.update(updated_data)
        return user

    @staticmethod
    def delete_user(user: dict) -> None:
        users_db.remove(user)
