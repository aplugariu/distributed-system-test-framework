from app.db import SessionLocal
from app.models import DeviceStatus
from app.service import create_device


def test_device_starts_in_created_state():
    with SessionLocal() as db:
        device = create_device(db, "integration-device")
        assert device.status == DeviceStatus.CREATED
