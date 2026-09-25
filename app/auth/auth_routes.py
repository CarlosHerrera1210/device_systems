from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth_service import AuthService
from app.dependencies.auth_dependency import CurrentUser
from app.dependencies.database_dependency import get_db
from app.schemas.auth_schema import AuthUserResponse, Token, UserRegister
from app.security.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED, summary="Registrar usuario")
@limiter.limit("3/minute")
def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)) -> AuthUserResponse:
    return AuthService.register(db, user_data)


@router.post("/login", response_model=Token, summary="Iniciar sesión")
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    token = AuthService.authenticate(db, form_data.username, form_data.password)
    return Token(access_token=token)


@router.get("/me", response_model=AuthUserResponse, summary="Consultar usuario autenticado")
def get_me(current_user: CurrentUser) -> AuthUserResponse:
    return current_user
