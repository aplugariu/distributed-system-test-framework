import uuid

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Device, DeviceStatus

QUEUE_NAME = "device-processing"


def create_device(db: Session, name: str) -> Device:
    device = Device(id=str(uuid.uuid4()), name=name, status=DeviceStatus.CREATED)
    db.add(device)
    db.commit()
    db.refresh(device)

    if settings.queue_enabled:
        from redis import Redis
        Redis.from_url(settings.redis_url, decode_responses=True).rpush(QUEUE_NAME, device.id)

    return device


def get_device(db: Session, device_id: str) -> Device | None:
    return db.get(Device, device_id)
