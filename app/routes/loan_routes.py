from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.loan_dependencies import get_loan_or_404
from app.dependencies.user_dependencies import get_user_or_404
from app.models.loan_model import Loan
from app.schemas.loan_schema import (
    LoanCreate,
    LoanDetailResponse,
    LoanDetailsListResponse,
    LoanListResponse,
    LoanResponse,
)
from app.services.device_service import DeviceService
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["Loans"])


def add_custom_headers(response: Response) -> None:
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "3.0.0"


@router.get(
    "",
    response_model=LoanListResponse,
    summary="Listar préstamos",
    description="Devuelve préstamos filtrados por estado, usuario, email o tipo de dispositivo.",
)
def list_loans(
    response: Response,
    status_filter: Optional[str] = Query(default=None, alias="status", description="Estado del préstamo"),
    user_email: Optional[str] = Query(default=None, description="Filtrar por email del usuario"),
    device_type: Optional[str] = Query(default=None, description="Filtrar por tipo de dispositivo"),
    user_id: Optional[int] = Query(default=None, description="Filtrar por usuario"),
    device_id: Optional[int] = Query(default=None, description="Filtrar por dispositivo"),
    db: Session = Depends(get_db),
) -> LoanListResponse:
    add_custom_headers(response)
    loans = LoanService.get_all_loans(
        db,
        status=status_filter,
        user_email=user_email,
        device_type=device_type,
        user_id=user_id,
        device_id=device_id,
    )
    return LoanListResponse(total=len(loans), loans=loans)


@router.get(
    "/details",
    response_model=LoanDetailsListResponse,
    summary="Consultar detalles de préstamos",
    description="Combina información de usuario y dispositivo usando joins para consultar préstamos relacionados.",
)
def list_loan_details(
    response: Response,
    status: Optional[str] = Query(default=None, description="Filtrar por estado"),
    user_email: Optional[str] = Query(default=None, description="Filtrar por correo del usuario"),
    device_type: Optional[str] = Query(default=None, description="Filtrar por tipo de dispositivo"),
    user_id: Optional[int] = Query(default=None, description="Filtrar por usuario"),
    device_id: Optional[int] = Query(default=None, description="Filtrar por dispositivo"),
    db: Session = Depends(get_db),
) -> LoanDetailsListResponse:
    add_custom_headers(response)
    loans = LoanService.get_loans_details(
        db,
        status=status,
        user_email=user_email,
        device_type=device_type,
        user_id=user_id,
        device_id=device_id,
    )
    return LoanDetailsListResponse(total=len(loans), loans=loans)


@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Consultar préstamo por ID",
    description="Devuelve la información básica de un préstamo específico.",
)
def get_loan(response: Response, loan: Loan = Depends(get_loan_or_404)) -> Loan:
    add_custom_headers(response)
    return loan


@router.get(
    "/user/{user_id}",
    response_model=LoanListResponse,
    summary="Consultar préstamos por usuario",
    description="Devuelve todos los préstamos registrados para un usuario.",
)
def get_user_loans(
    response: Response,
    user_id: int,
    db: Session = Depends(get_db),
) -> LoanListResponse:
    add_custom_headers(response)
    get_user_or_404(user_id, db)
    loans = LoanService.get_user_loans(db, user_id)
    return LoanListResponse(total=len(loans), loans=loans)


@router.get(
    "/device/{device_id}",
    response_model=LoanListResponse,
    summary="Consultar historial por dispositivo",
    description="Muestra el historial de préstamos asociado a un dispositivo.",
)
def get_device_loans(
    response: Response,
    device_id: int,
    db: Session = Depends(get_db),
) -> LoanListResponse:
    add_custom_headers(response)
    DeviceService.get_device_by_id(db, device_id)
    loans = LoanService.get_device_loans(db, device_id)
    return LoanListResponse(total=len(loans), loans=loans)


@router.post(
    "",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear préstamo",
    description="Crea un préstamo validando usuario y disponibilidad del dispositivo.",
)
def create_loan(
    loan_data: LoanCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> Loan:
    add_custom_headers(response)
    return LoanService.create_loan(db, loan_data)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Devolver dispositivo",
    description="Marca el préstamo como devuelto y vuelve a poner disponible el equipo.",
)
def return_loan(
    response: Response,
    loan: Loan = Depends(get_loan_or_404),
    db: Session = Depends(get_db),
) -> Loan:
    add_custom_headers(response)
    return LoanService.return_loan(db, loan)
