import os
import time

from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Device, DeviceStatus
from app.service import QUEUE_NAME

from redis.exceptions import RedisError

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://tester:tester@postgres:5432/testlab",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
PROCESSING_DELAY = float(os.getenv("PROCESSING_DELAY", "1.0"))
FAIL_DEVICE_NAME = os.getenv("FAIL_DEVICE_NAME", "force-failure")

PROCESSING_QUEUE_NAME = f"{QUEUE_NAME}:processing"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)


def process_device(device_id: str) -> None:
    with SessionLocal() as db:
        device = db.get(Device, device_id)

        if not device:
            return

        if device.status in {DeviceStatus.READY, DeviceStatus.FAILED}:
            return

        device.processing_count += 1
        device.status = DeviceStatus.PROCESSING
        db.commit()

        time.sleep(PROCESSING_DELAY)

        device.status = (
            DeviceStatus.FAILED
            if device.name == FAIL_DEVICE_NAME
            else DeviceStatus.READY
        )
        db.commit()


def recover_pending_items() -> None:
    while True:
        device_id = redis_client.rpoplpush(
            PROCESSING_QUEUE_NAME,
            QUEUE_NAME,
        )

        if device_id is None:
            break

        print(f"Recovered pending device: {device_id}")


def run() -> None:
    recover_pending_items()

    while True:
        try:
            device_id = redis_client.brpoplpush(
                QUEUE_NAME,
                PROCESSING_QUEUE_NAME,
                timeout=5,
            )

            if device_id is None:
                continue

            process_device(device_id)

            redis_client.lrem(
                PROCESSING_QUEUE_NAME,
                1,
                device_id,
            )

        except RedisError as exc:
            print(f"Redis unavailable: {exc}")
            time.sleep(2)

        except Exception as exc:
            print(f"Processing failed: {exc}")
            time.sleep(1)


if __name__ == "__main__":
    run()