import subprocess
import time

import httpx


BASE_URL = "http://localhost:8000"


def wait_for_status(device_id: str, expected_status: str, timeout: float = 15.0):
    deadline = time.time() + timeout

    while time.time() < deadline:
        response = httpx.get(
            f"{BASE_URL}/devices/{device_id}",
            timeout=2,
        )

        if response.status_code == 200:
            if response.json()["status"] == expected_status:
                return

        time.sleep(0.25)

    raise AssertionError(
        f"Device {device_id} did not reach status {expected_status}"
    )


def test_system_recovers_after_redis_outage():
    # fault injection: Redis unavailable
    subprocess.run(
        ["docker", "compose", "stop", "redis"],
        check=True,
    )

    time.sleep(1)

    # API should fail because it cannot enqueue the job
    failed_response = httpx.post(
        f"{BASE_URL}/devices",
        json={"name": "redis-down-device"},
        timeout=5,
    )

    assert failed_response.status_code >= 500

    # recovery: bring Redis back
    subprocess.run(
        ["docker", "compose", "start", "redis"],
        check=True,
    )

    time.sleep(2)

    # system should accept work again
    response = httpx.post(
        f"{BASE_URL}/devices",
        json={"name": "redis-recovered-device"},
        timeout=5,
    )

    response.raise_for_status()

    device_id = response.json()["id"]

    wait_for_status(device_id, "READY", timeout=20)