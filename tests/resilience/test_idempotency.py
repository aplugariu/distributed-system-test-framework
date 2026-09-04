import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Device
from tests.framework.api_client import create_device
from tests.framework.redis_control import enqueue_device
from tests.framework.waiters import wait_for_status


DATABASE_URL = "postgresql+psycopg://tester:tester@localhost:5432/testlab"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_processing_count(device_id: str) -> int:
    with SessionLocal() as db:
        device = db.get(Device, device_id)
        return device.processing_count


def test_duplicate_job_is_ignored_after_completion():
    device = create_device("idempotency-test-device")
    device_id = device["id"]

    wait_for_status(device_id, "READY", timeout=20)

    assert get_processing_count(device_id) == 1

    enqueue_device(device_id)

    time.sleep(2)

    assert get_processing_count(device_id) == 1