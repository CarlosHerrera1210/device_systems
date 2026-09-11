from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schema import Role, UserCreate, UserPatch, UserUpdate


class UserService:
    @staticmethod
    def get_all_users(
        db: Session,
        role: Role | None = None,
        is_active: bool | None = None,
        order_by: str = "created_at",
    ) -> list[User]:
        statement = select(User)

        if role is not None:
            statement = statement.where(User.role == role)

        if is_active is not None:
            statement = statement.where(User.is_active == is_active)

        if order_by == "name":
            statement = statement.order_by(User.name.asc())
        else:
            statement = statement.order_by(User.created_at.desc())

        return list(db.scalars(statement).all())

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        statement = select(User).where(User.email == email.lower())
        return db.scalar(statement)

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        if UserService.get_user_by_email(db, str(user_data.email)) is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correo electrónico duplicado",
            )

        new_user = User(
            name=user_data.name,
            email=str(user_data.email).lower(),
            role=user_data.role,
            is_active=user_data.is_active,
        )
        db.add(new_user)

        try:
            db.commit()
        except IntegrityError as error:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correo electrónico duplicado",
            ) from error

        db.refresh(new_user)
        return new_user

    @staticmethod
    def update_user_full(db: Session, user: User, user_data: UserUpdate) -> User:
        UserService._validate_unique_email(db, str(user_data.email), current_user_id=user.id)

        user.name = user_data.name
        user.email = str(user_data.email).lower()
        user.role = user_data.role
        user.is_active = user_data.is_active

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user_partial(db: Session, user: User, user_data: UserPatch) -> User:
        updated_data = user_data.model_dump(exclude_unset=True)

        if not updated_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe enviar al menos un campo para actualizar",
            )

        if "email" in updated_data:
            updated_data["email"] = str(updated_data["email"]).lower()
            UserService._validate_unique_email(db, updated_data["email"], current_user_id=user.id)

        for field, value in updated_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user: User) -> None:
        db.delete(user)
        db.commit()

    @staticmethod
    def _validate_unique_email(db: Session, email: str, current_user_id: int) -> None:
        existing_user = UserService.get_user_by_email(db, email)

        if existing_user is not None and existing_user.id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correo electrónico duplicado",
            )
