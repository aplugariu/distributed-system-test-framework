import time
import uuid

from app.config import settings
from app.models import Device, DeviceStatus
from app.queue.redis_stream_queue import RedisStreamQueue
from worker.stream_worker import (
    SessionLocal,
    mark_processing,
    process_message,
)


def test_stale_processing_job_is_recovered_by_second_consumer():
    stream_name = f"test-stream-{uuid.uuid4()}"

    queue = RedisStreamQueue(
        settings.redis_url,
        stream_name=stream_name,
    )

    queue.ensure_group()

    device_id = str(uuid.uuid4())

    with SessionLocal() as db:
        device = Device(
            id=device_id,
            name="stream-failover-device",
            status=DeviceStatus.CREATED,
        )
        db.add(device)
        db.commit()

    message_id = queue.enqueue(
        device_id=device_id,
        correlation_id="failover-test",
    )

    consumed = queue.read_new_message(
        consumer_name="consumer-1",
    )

    assert consumed is not None

    consumed_id, payload = consumed
    assert consumed_id == message_id

    # consumer-1 started work
    mark_processing(device_id)

    with SessionLocal() as db:
        processing_device = db.get(Device, device_id)
        assert processing_device.status == DeviceStatus.PROCESSING
        assert processing_device.processing_count == 1

    # no ACK -> simulate crash
    time.sleep(1.1)

    claimed = queue.claim_stale_messages(
        consumer_name="consumer-2",
        min_idle_time_ms=1000,
    )

    _, messages, *_ = claimed

    assert len(messages) == 1

    claimed_id, claimed_payload = messages[0]

    process_message(
        claimed_id,
        claimed_payload,
        stream_queue=queue,
    )

    with SessionLocal() as db:
        final_device = db.get(Device, device_id)

        assert final_device.status == DeviceStatus.READY
        assert final_device.processing_count == 2