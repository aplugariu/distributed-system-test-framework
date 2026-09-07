from app.config import settings
from app.queue.redis_stream_queue import RedisStreamQueue
from redis import Redis
from redis.exceptions import ResponseError
import uuid
import time

def test_stream_job_can_be_enqueued():
    stream_name = f"test-stream-{uuid.uuid4()}"

    queue = RedisStreamQueue(
        settings.redis_url,
        stream_name=stream_name,
    )


def test_stream_job_can_be_consumed_and_acknowledged():
    stream_name = f"test-stream-{uuid.uuid4()}"

    queue = RedisStreamQueue(
        settings.redis_url,
        stream_name=stream_name,
    )

    queue.ensure_group()

    message_id = queue.enqueue(
        device_id="stream-consume-device",
        correlation_id="stream-test",
    )

    consumed = queue.read_new_message(
        consumer_name="test-consumer",
    )

    assert consumed is not None

    consumed_id, payload = consumed

    assert consumed_id == message_id
    assert payload["device_id"] == "stream-consume-device"

    ack_count = queue.ack_message(consumed_id)

    assert ack_count == 1


def test_stale_stream_job_can_be_claimed_by_another_consumer():
    stream_name = f"test-stream-{uuid.uuid4()}"

    queue = RedisStreamQueue(
        settings.redis_url,
        stream_name=stream_name,
    )

    queue.ensure_group()

    message_id = queue.enqueue(
        device_id="stale-stream-device",
        correlation_id="stale-test",
    )

    consumed = queue.read_new_message(
        consumer_name="consumer-1",
    )

    assert consumed is not None

    consumed_id, payload = consumed

    assert consumed_id == message_id
    assert payload["device_id"] == "stale-stream-device"

    # consumer-1 does NOT ACK the message
    time.sleep(1.1)

    claimed = queue.claim_stale_messages(
        consumer_name="consumer-2",
        min_idle_time_ms=1000,
    )

    next_start_id, messages, deleted_ids = claimed

    assert len(messages) == 1

    claimed_id, claimed_payload = messages[0]

    assert claimed_id == message_id
    assert claimed_payload["device_id"] == "stale-stream-device"

    ack_count = queue.ack_message(claimed_id)

    assert ack_count == 1

