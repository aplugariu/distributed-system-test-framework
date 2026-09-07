import os
import socket
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Device, DeviceStatus
from app.queue.redis_stream_queue import RedisStreamQueue
from app.config import settings

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://tester:tester@postgres:5432/testlab",
)

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://redis:6379/0",
)

PROCESSING_DELAY = float(
    os.getenv("PROCESSING_DELAY", "1.0")
)

FAIL_DEVICE_NAME = os.getenv(
    "FAIL_DEVICE_NAME",
    "force-failure",
)

CONSUMER_NAME = socket.gethostname()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

queue = RedisStreamQueue(REDIS_URL)


def process_device(
    device_id: str,
    correlation_id: str | None = None,
) -> None:
    with SessionLocal() as db:
        device = db.get(Device, device_id)

        print(
            f"STREAM WORKER device={device} device_id={device_id}",
            flush=True,
        )

        if not device:
            return

        if device.status in {
            DeviceStatus.READY,
            DeviceStatus.FAILED,
        }:
            return

        device.processing_count += 1
        device.status = DeviceStatus.PROCESSING
        db.commit()

        print(
            f"service=stream-worker "
            f"event=processing_started "
            f"consumer={CONSUMER_NAME} "
            f"correlation_id={correlation_id} "
            f"device_id={device_id} "
            f"processing_count={device.processing_count}",
            flush=True,
        )

        time.sleep(PROCESSING_DELAY)

        device.status = (
            DeviceStatus.FAILED
            if device.name == FAIL_DEVICE_NAME
            else DeviceStatus.READY
        )

        db.commit()

        print(
            f"service=stream-worker "
            f"event=processing_completed "
            f"consumer={CONSUMER_NAME} "
            f"correlation_id={correlation_id} "
            f"device_id={device_id} "
            f"status={device.status.value} "
            f"processing_count={device.processing_count}",
            flush=True,
        )
def process_message(
    message_id: str,
    payload: dict,
    stream_queue: RedisStreamQueue = queue,
) -> None:
    device_id = payload["device_id"]
    correlation_id = payload.get("correlation_id") or None

    process_device(
        device_id,
        correlation_id,
    )

    stream_queue.ack_message(message_id)


def recover_stale_messages() -> None:
    claimed = queue.claim_stale_messages(
        consumer_name=CONSUMER_NAME,
        min_idle_time_ms=3000,
    )

    _, messages, *_ = claimed

    for message_id, payload in messages:
        print(
            f"service=stream-worker "
            f"event=stale_job_claimed "
            f"consumer={CONSUMER_NAME} "
            f"device_id={payload['device_id']}",
            flush=True,
        )

        process_message(
            message_id,
            payload,
        )


def run() -> None:
    queue.ensure_group()

    while True:
        try:
            recover_stale_messages()

            message = queue.read_new_message(
                consumer_name=CONSUMER_NAME,
                block_ms=1000,
            )

            if message is None:
                continue

            message_id, payload = message

            process_message(
                message_id,
                payload,
            )

        except Exception as exc:
            print(
                f"service=stream-worker "
                f"event=processing_error "
                f"consumer={CONSUMER_NAME} "
                f"error={exc}",
                flush=True,
            )

            time.sleep(1)


if __name__ == "__main__":
    run()
