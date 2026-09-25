from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LoanCreate(BaseModel):
    user_id: int = Field(..., gt=0, examples=[1])
    device_id: int = Field(..., gt=0, examples=[1])
    status: str = Field(default="active", examples=["active"])
    loan_date: datetime | None = Field(default=None, examples=["2026-09-15T12:00:00Z"])
    return_date: datetime | None = Field(default=None, examples=["2026-09-20T12:00:00Z"])


class LoanUpdate(BaseModel):
    user_id: int = Field(..., gt=0, examples=[1])
    device_id: int = Field(..., gt=0, examples=[1])
    status: str = Field(..., examples=["active"])
    return_date: datetime | None = Field(default=None, examples=["2026-09-20T12:00:00Z"])


class LoanPatch(BaseModel):
    user_id: int | None = Field(default=None, gt=0, examples=[1])
    device_id: int | None = Field(default=None, gt=0, examples=[1])
    status: str | None = Field(default=None, examples=["returned"])
    return_date: datetime | None = Field(default=None, examples=["2026-09-20T12:00:00Z"])


class UserSummary(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class DeviceSummary(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str

    model_config = ConfigDict(from_attributes=True)


class LoanResponse(BaseModel):
    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: datetime | None
    status: str

    model_config = ConfigDict(from_attributes=True)


class LoanDetailResponse(BaseModel):
    loan_id: int
    status: str
    loan_date: datetime
    return_date: datetime | None
    user: UserSummary
    device: DeviceSummary


class LoanListResponse(BaseModel):
    total: int
    loans: list[LoanResponse]


class LoanDetailsListResponse(BaseModel):
    total: int
    loans: list[LoanDetailResponse]
