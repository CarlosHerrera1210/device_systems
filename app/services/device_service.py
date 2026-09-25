from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceUpdate


class DeviceService:
    @staticmethod
    def get_all_devices(
        db: Session,
        device_type: str | None = None,
        is_available: bool | None = None,
        brand: str | None = None,
        search: str | None = None,
        order_by: str = "created_at",
    ) -> list[Device]:
        statement = select(Device)

        if device_type is not None:
            statement = statement.where(Device.device_type == device_type.lower())

        if is_available is not None:
            statement = statement.where(Device.is_available == is_available)

        if brand is not None:
            statement = statement.where(Device.brand.ilike(f"%{brand}%"))

        if search is not None:
            statement = statement.where(
                or_(
                    Device.name.ilike(f"%{search}%"),
                    Device.serial_number.ilike(f"%{search}%"),
                    Device.device_type.ilike(f"%{search}%"),
                )
            )

        if order_by == "name":
            statement = statement.order_by(Device.name.asc())
        else:
            statement = statement.order_by(Device.created_at.desc())

        return list(db.scalars(statement).all())

    @staticmethod
    def get_device_by_id(db: Session, device_id: int) -> Device | None:
        return db.get(Device, device_id)

    @staticmethod
    def get_device_by_serial(db: Session, serial_number: str) -> Device | None:
        statement = select(Device).where(Device.serial_number == serial_number)
        return db.scalar(statement)

    @staticmethod
    def create_device(db: Session, device_data: DeviceCreate) -> Device:
        if DeviceService.get_device_by_serial(db, device_data.serial_number) is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de serie duplicado",
            )

        new_device = Device(
            name=device_data.name,
            serial_number=device_data.serial_number,
            device_type=device_data.device_type.lower(),
            brand=device_data.brand,
            is_available=device_data.is_available,
        )
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        return new_device

    @staticmethod
    def update_device_full(db: Session, device: Device, device_data: DeviceUpdate) -> Device:
        DeviceService._validate_unique_serial(db, device_data.serial_number, current_device_id=device.id)

        device.name = device_data.name
        device.serial_number = device_data.serial_number
        device.device_type = device_data.device_type.lower()
        device.brand = device_data.brand
        device.is_available = device_data.is_available

        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def update_device_partial(db: Session, device: Device, device_data: DevicePatch) -> Device:
        updated_data = device_data.model_dump(exclude_unset=True)

        if not updated_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe enviar al menos un campo para actualizar",
            )

        if "serial_number" in updated_data:
            DeviceService._validate_unique_serial(db, updated_data["serial_number"], current_device_id=device.id)

        if "device_type" in updated_data:
            updated_data["device_type"] = str(updated_data["device_type"]).lower()

        for field, value in updated_data.items():
            setattr(device, field, value)

        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def delete_device(db: Session, device: Device) -> None:
        db.delete(device)
        db.commit()

    @staticmethod
    def _validate_unique_serial(db: Session, serial_number: str, current_device_id: int) -> None:
        existing_device = DeviceService.get_device_by_serial(db, serial_number)

        if existing_device is not None and existing_device.id != current_device_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de serie duplicado",
            )
