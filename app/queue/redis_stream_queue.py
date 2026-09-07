from redis import Redis
from redis.exceptions import ResponseError


STREAM_NAME = "device-processing-stream"
CONSUMER_GROUP = "device-workers"

class RedisStreamQueue:
    def __init__(
        self,
        redis_url: str,
        stream_name: str = STREAM_NAME,
    ):
        self.redis = Redis.from_url(
            redis_url,
            decode_responses=True,
        )
        self.stream_name = stream_name

    def ensure_group(self) -> None:
        try:
            self.redis.xgroup_create(
                self.stream_name,
                CONSUMER_GROUP,
                id="0",
                mkstream=True,
            )
        except ResponseError as exc:
            if "BUSYGROUP" not in str(exc):
                raise

                    
                     
    def enqueue(
        self,
        device_id: str,
        correlation_id: str | None = None,
    ) -> str:
        message_id = self.redis.xadd(
            self.stream_name,
            {
                "device_id": device_id,
                "correlation_id": correlation_id or "",
            },
        )

        return message_id

    def read_new_message(
        self,
        consumer_name: str,
        block_ms: int = 5000,
    ):
        messages = self.redis.xreadgroup(
            groupname=CONSUMER_GROUP,
            consumername=consumer_name,
            streams={self.stream_name: ">"},
            count=1,
            block=block_ms,
        )

        if not messages:
            return None

        _, entries = messages[0]
        message_id, payload = entries[0]

        return message_id, payload

    def ack_message(self, message_id: str) -> int:
        return self.redis.xack(
            self.stream_name,
            CONSUMER_GROUP,
            message_id,
        )

    def claim_stale_messages(
    self,
    consumer_name: str,
    min_idle_time_ms: int = 1000,
):
        return self.redis.xautoclaim(
        self.stream_name,
        CONSUMER_GROUP,
        consumer_name,
        min_idle_time_ms,
        "0-0",
        count=10,
    )
