import uuid

from app.models import Device, DeviceStatus
from app.queue.redis_stream_queue import RedisStreamQueue
from worker.stream_worker import SessionLocal, process_message
from app.config import settings

def test_stream_worker_processes_and_acknowledges_job():
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
            name="stream-worker-device",
            status=DeviceStatus.CREATED,
        )
        db.add(device)
        db.commit()

    message_id = queue.enqueue(
        device_id=device_id,
        correlation_id="stream-worker-test",
    )

    consumed = queue.read_new_message(
        consumer_name="test-stream-worker",
    )

    assert consumed is not None

    consumed_id, payload = consumed
    assert consumed_id == message_id

    process_message(
        consumed_id,
        payload,
        stream_queue=queue,
    )

    with SessionLocal() as db:
        final_device = db.get(Device, device_id)

        assert final_device is not None
        assert final_device.status == DeviceStatus.READY
        assert final_device.processing_count == 1