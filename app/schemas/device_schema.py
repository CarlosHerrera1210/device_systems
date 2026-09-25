from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=2, examples=["Laptop Lenovo ThinkPad"])
    serial_number: str = Field(..., min_length=3, examples=["LEN-2024-001"])
    device_type: str = Field(..., examples=["laptop"])
    brand: str | None = Field(default=None, examples=["Lenovo"])
    is_available: bool = Field(default=True, examples=[True])


class DeviceUpdate(BaseModel):
    name: str = Field(..., min_length=2, examples=["Laptop Lenovo ThinkPad"])
    serial_number: str = Field(..., min_length=3, examples=["LEN-2024-001"])
    device_type: str = Field(..., examples=["laptop"])
    brand: str | None = Field(default=None, examples=["Lenovo"])
    is_available: bool = Field(..., examples=[True])


class DevicePatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, examples=["Laptop Lenovo ThinkPad"])
    serial_number: str | None = Field(default=None, min_length=3, examples=["LEN-2024-001"])
    device_type: str | None = Field(default=None, examples=["laptop"])
    brand: str | None = Field(default=None, examples=["Lenovo"])
    is_available: bool | None = Field(default=None, examples=[True])


class DeviceResponse(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str
    brand: str | None
    is_available: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviceListResponse(BaseModel):
    total: int
    devices: list[DeviceResponse]
