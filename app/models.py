import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class DeviceStatus(str, enum.Enum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[DeviceStatus] = mapped_column(Enum(DeviceStatus), default=DeviceStatus.CREATED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    processing_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
