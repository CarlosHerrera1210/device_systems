from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (
        CheckConstraint(
            "device_type IN ('laptop', 'tablet', 'proyector', 'camara', 'router', 'monitor')",
            name="ck_devices_type_allowed",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    device_type: Mapped[str] = mapped_column(String(30), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    loans: Mapped[list["Loan"]] = relationship("Loan", back_populates="device")
