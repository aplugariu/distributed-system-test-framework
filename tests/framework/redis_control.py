from redis import Redis

REDIS_URL = "redis://localhost:6379/0"
QUEUE_NAME = "device-processing"


def enqueue_device(device_id: str) -> None:
    redis_client = Redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )

    redis_client.rpush(
        QUEUE_NAME,
        device_id,
    )