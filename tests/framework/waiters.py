import time

from tests.framework.api_client import get_device


def wait_for_status(
    device_id: str,
    expected_status: str,
    timeout: float = 15.0,
) -> None:
    deadline = time.time() + timeout

    while time.time() < deadline:
        device = get_device(device_id)

        if device["status"] == expected_status:
            return

        time.sleep(0.25)

    raise AssertionError(
        f"Device {device_id} did not reach status {expected_status}"
    )