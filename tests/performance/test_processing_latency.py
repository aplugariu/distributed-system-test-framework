import time

from tests.framework.api_client import create_device
from tests.framework.waiters import wait_for_status


def test_device_processing_latency_is_within_threshold():
    start = time.monotonic()

    device = create_device("latency-test-device")

    final_device = wait_for_status(
        device["id"],
        "READY",
        timeout=10,
    )

    elapsed = time.monotonic() - start

    assert final_device["status"] == "READY"
    assert elapsed < 6.0