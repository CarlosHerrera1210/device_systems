from typing import Optional

from fastapi import APIRouter, Depends, Header, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import get_user_or_404
from app.models.user_model import User
from app.schemas.user_schema import (
    Role,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
    UserPatch,
)
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


def add_custom_headers(response: Response) -> None:
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "3.0.0"


@router.get(
    "",
    response_model=UserListResponse,
    summary="Listar usuarios",
    description="Devuelve la lista de usuarios, con posibilidad de filtrar por rol o estado activo.",
    response_description="Lista de usuarios y total de resultados.",
)
def list_users(
    response: Response,
    role: Optional[Role] = Query(default=None, description="Filtrar usuarios por rol"),
    is_active: Optional[bool] = Query(default=None, description="Filtrar por estado activo"),
    order_by: str = Query(default="created_at", pattern="^(name|created_at)$"),
    user_agent: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> UserListResponse:
    add_custom_headers(response)
    filtered_users = UserService.get_all_users(
        db,
        role=role,
        is_active=is_active,
        order_by=order_by,
    )

    if user_agent:
        response.headers["X-Client-Detected"] = "true"

    return UserListResponse(total=len(filtered_users), users=filtered_users)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
    description="Devuelve un usuario específico según su identificador.",
    response_description="Usuario encontrado.",
)
def get_user(response: Response, user: User = Depends(get_user_or_404)) -> User:
    add_custom_headers(response)
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Registra un nuevo usuario con validación de datos y control de correos duplicados.",
    response_description="Usuario creado correctamente.",
)
def create_user(
    user: UserCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> User:
    add_custom_headers(response)
    return UserService.create_user(db, user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario completo",
    description="Reemplaza completamente la información de un usuario existente.",
    response_description="Usuario actualizado.",
)
def update_user_full(
    user_data: UserUpdate,
    response: Response,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> User:
    add_custom_headers(response)
    return UserService.update_user_full(db, user, user_data)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario parcialmente",
    description="Modifica solo los campos enviados por el cliente para un usuario existente.",
    response_description="Usuario actualizado parcialmente.",
)
def update_user_partial(
    user_data: UserPatch,
    response: Response,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> User:
    add_custom_headers(response)
    return UserService.update_user_partial(db, user, user_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario existente según su identificador.",
    response_description="Usuario eliminado correctamente.",
)
def delete_user(
    response: Response,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> None:
    add_custom_headers(response)
    UserService.delete_user(db, user)
