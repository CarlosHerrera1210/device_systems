from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query, Response, status

from app.schemas.user_schema import Role, UserCreate, UserListResponse, UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


def get_initial_users() -> list[dict]:
    return [
        {
            "id": 1,
            "name": "Carlos Herrera",
            "email": "carlos@example.com",
            "role": "admin",
            "is_active": True,
        },
        {
            "id": 2,
            "name": "Laura Gomez",
            "email": "laura@example.com",
            "role": "support",
            "is_active": True,
        },
        {
            "id": 3,
            "name": "Andres Perez",
            "email": "andres@example.com",
            "role": "user",
            "is_active": False,
        },
    ]


users_db: list[dict] = get_initial_users()


def add_custom_headers(response: Response) -> None:
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"


def find_user_by_id(user_id: int) -> dict | None:
    return next((user for user in users_db if user["id"] == user_id), None)


def email_exists(email: str) -> bool:
    return any(user["email"].lower() == email.lower() for user in users_db)


@router.get("", response_model=UserListResponse)
def list_users(
    response: Response,
    role: Optional[Role] = Query(default=None, description="Filtrar usuarios por rol"),
    is_active: Optional[bool] = Query(default=None, description="Filtrar por estado activo"),
    user_agent: Optional[str] = Header(default=None),
) -> UserListResponse:
    add_custom_headers(response)

    filtered_users = users_db.copy()

    if role is not None:
        filtered_users = [user for user in filtered_users if user["role"] == role]

    if is_active is not None:
        filtered_users = [user for user in filtered_users if user["is_active"] == is_active]

    if user_agent:
        response.headers["X-Client-Detected"] = "true"

    return UserListResponse(total=len(filtered_users), users=filtered_users)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, response: Response) -> dict:
    add_custom_headers(response)
    user = find_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un usuario con id {user_id}.",
        )

    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, response: Response) -> dict:
    add_custom_headers(response)

    if email_exists(user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario registrado con ese correo.",
        )

    new_user = {
        "id": len(users_db) + 1,
        "name": user.name,
        "email": str(user.email),
        "role": user.role,
        "is_active": user.is_active,
    }
    users_db.append(new_user)

    return new_user

