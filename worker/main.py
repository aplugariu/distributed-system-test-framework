import os
import time

from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Device, DeviceStatus
from app.service import QUEUE_NAME

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://tester:tester@postgres:5432/testlab")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
PROCESSING_DELAY = float(os.getenv("PROCESSING_DELAY", "1.0"))
FAIL_DEVICE_NAME = os.getenv("FAIL_DEVICE_NAME", "force-failure")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)


def process_device(device_id: str) -> None:
    with SessionLocal() as db:
        device = db.get(Device, device_id)
        if not device:
            return

        device.status = DeviceStatus.PROCESSING
        db.commit()
        time.sleep(PROCESSING_DELAY)

        device.status = DeviceStatus.FAILED if device.name == FAIL_DEVICE_NAME else DeviceStatus.READY
        db.commit()


def run() -> None:
    while True:
        item = redis_client.blpop(QUEUE_NAME, timeout=5)
        if item:
            _, device_id = item
            process_device(device_id)


if __name__ == "__main__":
    run()
