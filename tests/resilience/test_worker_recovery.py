import time

from tests.framework.api_client import create_device
from tests.framework.docker_control import kill_service, start_service
from tests.framework.waiters import wait_for_status


def test_worker_recovers_job_after_crash():
    device = create_device("recovery-test-device")

    wait_for_status(device["id"], "PROCESSING")

    kill_service("worker")

    "time.sleep(1)"

    start_service("worker")

    recovered_device = wait_for_status(device["id"], "READY", timeout=20)

    assert recovered_device["status"] == "READY"
    assert recovered_device["processing_count"] == 2