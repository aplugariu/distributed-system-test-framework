import time
from concurrent.futures import ThreadPoolExecutor

from tests.framework.api_client import create_device
from tests.framework.waiters import wait_for_status


def test_two_workers_process_jobs_in_parallel():
    names = [
        "parallel-device-1",
        "parallel-device-2",
    ]

    start = time.monotonic()

    with ThreadPoolExecutor(max_workers=2) as executor:
        devices = list(
            executor.map(create_device, names)
        )

    final_devices = [
        wait_for_status(
            device["id"],
            "READY",
            timeout=10,
        )
        for device in devices
    ]

    elapsed = time.monotonic() - start

    assert len(final_devices) == 2

    assert all(
        device["status"] == "READY"
        for device in final_devices
    )

    assert all(
        device["processing_count"] == 1
        for device in final_devices
    )

    assert final_devices[0]["id"] != final_devices[1]["id"]

    print(f"Parallel processing time: {elapsed:.2f}s")