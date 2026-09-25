from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, get_password_hash, verify_password
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister
from app.services.user_service import UserService


class AuthService:
    @staticmethod
    def register(db: Session, user_data: UserRegister) -> User:
        if UserService.get_user_by_email(db, str(user_data.email)) is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Correo electrónico duplicado")

        user = User(
            name=user_data.name,
            email=str(user_data.email).lower(),
            hashed_password=get_password_hash(user_data.password),
            role=user_data.role,
            is_active=user_data.is_active,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> str:
        user = UserService.get_user_by_email(db, email)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")
        return create_access_token({"sub": str(user.id), "role": user.role})
