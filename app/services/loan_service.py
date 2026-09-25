from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.loan_schema import LoanCreate, LoanPatch


class LoanService:
    @staticmethod
    def get_all_loans(
        db: Session,
        status: str | None = None,
        user_email: str | None = None,
        device_type: str | None = None,
        user_id: int | None = None,
        device_id: int | None = None,
    ) -> list[Loan]:
        statement = select(Loan).join(User).join(Device)

        if status is not None:
            statement = statement.where(Loan.status == status.lower())

        if user_email is not None:
            statement = statement.where(User.email.ilike(f"%{user_email}%"))

        if device_type is not None:
            statement = statement.where(Device.device_type.ilike(f"%{device_type}%"))

        if user_id is not None:
            statement = statement.where(User.id == user_id)

        if device_id is not None:
            statement = statement.where(Device.id == device_id)

        return list(db.scalars(statement).all())

    @staticmethod
    def get_loan_by_id(db: Session, loan_id: int) -> Loan | None:
        return db.get(Loan, loan_id)

    @staticmethod
    def create_loan(db: Session, loan_data: LoanCreate) -> Loan:
        user = db.get(User, loan_data.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        device = db.get(Device, loan_data.device_id)
        if device is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")

        if not device.is_available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El dispositivo no está disponible para préstamo",
            )

        new_loan = Loan(
            user_id=loan_data.user_id,
            device_id=loan_data.device_id,
            loan_date=loan_data.loan_date or datetime.now(timezone.utc),
            status=loan_data.status.lower(),
        )
        db.add(new_loan)
        device.is_available = False
        db.commit()
        db.refresh(new_loan)
        return new_loan

    @staticmethod
    def return_loan(db: Session, loan: Loan) -> Loan:
        if loan.status == "returned":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El préstamo ya fue devuelto",
            )

        loan.status = "returned"
        loan.return_date = datetime.now(timezone.utc)
        loan.device.is_available = True
        db.commit()
        db.refresh(loan)
        return loan

    @staticmethod
    def get_loans_details(db: Session, **filters) -> list[dict]:
        statement = (
            select(
                Loan.id.label("loan_id"),
                Loan.status,
                Loan.loan_date,
                Loan.return_date,
                User.id.label("user_id"),
                User.name.label("user_name"),
                User.email.label("user_email"),
                Device.id.label("device_id"),
                Device.name.label("device_name"),
                Device.serial_number,
                Device.device_type,
            )
            .select_from(Loan)
            .join(User, Loan.user_id == User.id)
            .join(Device, Loan.device_id == Device.id)
        )

        if filters.get("status"):
            statement = statement.where(Loan.status == filters["status"].lower())

        if filters.get("user_email"):
            statement = statement.where(User.email.ilike(f"%{filters['user_email']}%"))

        if filters.get("device_type"):
            statement = statement.where(Device.device_type.ilike(f"%{filters['device_type']}%"))

        if filters.get("user_id") is not None:
            statement = statement.where(User.id == filters["user_id"])

        if filters.get("device_id") is not None:
            statement = statement.where(Device.id == filters["device_id"])

        rows = db.execute(statement).all()
        return [
            {
                "loan_id": row.loan_id,
                "status": row.status,
                "loan_date": row.loan_date,
                "return_date": row.return_date,
                "user": {"id": row.user_id, "name": row.user_name, "email": row.user_email},
                "device": {
                    "id": row.device_id,
                    "name": row.device_name,
                    "serial_number": row.serial_number,
                    "device_type": row.device_type,
                },
            }
            for row in rows
        ]

    @staticmethod
    def get_user_loans(db: Session, user_id: int) -> list[Loan]:
        statement = select(Loan).where(Loan.user_id == user_id).order_by(Loan.loan_date.desc())
        return list(db.scalars(statement).all())

    @staticmethod
    def get_device_loans(db: Session, device_id: int) -> list[Loan]:
        statement = select(Loan).where(Loan.device_id == device_id).order_by(Loan.loan_date.desc())
        return list(db.scalars(statement).all())
