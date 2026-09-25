from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.device_dependencies import get_device_or_404
from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DeviceListResponse, DevicePatch, DeviceResponse, DeviceUpdate
from app.schemas.loan_schema import LoanListResponse
from app.services.device_service import DeviceService
from app.services.loan_service import LoanService

router = APIRouter(prefix="/devices", tags=["Devices"])


def add_custom_headers(response: Response) -> None:
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "3.0.0"


@router.get(
    "",
    response_model=DeviceListResponse,
    summary="Listar dispositivos",
    description="Devuelve dispositivos con filtros por tipo, disponibilidad, marca o texto libre.",
)
def list_devices(
    response: Response,
    device_type: Optional[str] = Query(default=None, description="Filtrar por tipo de dispositivo"),
    is_available: Optional[bool] = Query(default=None, description="Filtrar por disponibilidad"),
    brand: Optional[str] = Query(default=None, description="Filtrar por marca"),
    search: Optional[str] = Query(default=None, description="Buscar por nombre, serial o tipo"),
    order_by: str = Query(default="created_at", pattern="^(name|created_at)$"),
    db: Session = Depends(get_db),
)-> DeviceListResponse:
    add_custom_headers(response)
    devices = DeviceService.get_all_devices(
        db,
        device_type=device_type,
        is_available=is_available,
        brand=brand,
        search=search,
        order_by=order_by,
    )
    return DeviceListResponse(total=len(devices), devices=devices)


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Consultar dispositivo por ID",
    description="Devuelve la información de un dispositivo específico.",
)
def get_device(response: Response, device: Device = Depends(get_device_or_404)) -> Device:
    add_custom_headers(response)
    return device


@router.get(
    "/{device_id}/loans",
    response_model=LoanListResponse,
    summary="Consultar historial de un dispositivo",
    description="Muestra el historial de préstamos asociado a un dispositivo.",
    response_description="Historial de préstamos del dispositivo.",
)
def get_device_loans(
    response: Response,
    device_id: int,
    db: Session = Depends(get_db),
) -> LoanListResponse:
    add_custom_headers(response)
    get_device_or_404(device_id, db)
    loans = LoanService.get_device_loans(db, device_id)
    return LoanListResponse(total=len(loans), loans=loans)


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear dispositivo",
    description="Registra un nuevo equipo tecnológico con número de serie único.",
)
def create_device(
    device_data: DeviceCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> Device:
    add_custom_headers(response)
    return DeviceService.create_device(db, device_data)


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo completo",
    description="Reemplaza la información completa de un dispositivo existente.",
)
def update_device_full(
    device_data: DeviceUpdate,
    response: Response,
    device: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> Device:
    add_custom_headers(response)
    return DeviceService.update_device_full(db, device, device_data)


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo parcialmente",
    description="Actualiza solo los campos enviados por el cliente.",
)
def update_device_partial(
    device_data: DevicePatch,
    response: Response,
    device: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> Device:
    add_custom_headers(response)
    return DeviceService.update_device_partial(db, device, device_data)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar dispositivo",
    description="Elimina un dispositivo existente si ya no se necesita.",
)
def delete_device(
    response: Response,
    device: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> None:
    add_custom_headers(response)
    DeviceService.delete_device(db, device)
