import json
import uuid

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Device, DeviceStatus

QUEUE_NAME = "device-processing"


def create_device(
    db: Session,
    name: str,
    correlation_id: str | None = None,
) -> Device:
    device = Device(
        id=str(uuid.uuid4()),
        name=name,
        status=DeviceStatus.CREATED,
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    if settings.queue_enabled:
        from redis import Redis

        payload = {
            "device_id": device.id,
            "correlation_id": correlation_id,
        }

        Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        ).rpush(
            QUEUE_NAME,
            json.dumps(payload),
        )
        print(
    f"service=api "
    f"event=job_queued "
    f"correlation_id={correlation_id} "
    f"device_id={device.id} "
    f"status={device.status.value}",
    flush=True,
)
    return device


def get_device(db: Session, device_id: str) -> Device | None:
    return db.get(Device, device_id)