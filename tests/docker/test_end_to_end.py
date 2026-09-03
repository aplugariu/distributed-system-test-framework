import os
import time

import httpx

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def wait_for_status(device_id: str, expected: str, timeout: float = 10.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = httpx.get(f"{BASE_URL}/devices/{device_id}", timeout=2)
        response.raise_for_status()
        if response.json()["status"] == expected:
            return response.json()
        time.sleep(0.25)
    raise AssertionError(f"Device {device_id} did not reach {expected} within {timeout}s")


def test_device_reaches_ready_state():
    response = httpx.post(f"{BASE_URL}/devices", json={"name": "camera-ecu"}, timeout=2)
    response.raise_for_status()
    device = response.json()

    final = wait_for_status(device["id"], "READY")
    assert final["name"] == "camera-ecu"


def test_failure_path_is_observable():
    response = httpx.post(f"{BASE_URL}/devices", json={"name": "force-failure"}, timeout=2)
    response.raise_for_status()
    device = response.json()

    final = wait_for_status(device["id"], "FAILED")
    assert final["status"] == "FAILED"
