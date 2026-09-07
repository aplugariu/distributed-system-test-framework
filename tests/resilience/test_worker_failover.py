from tests.framework.api_client import create_device
from tests.framework.docker_control import (
    get_worker_containers,
    kill_container,
)
from tests.framework.waiters import wait_for_status


def test_job_recovers_when_one_of_two_workers_crashes():
    workers = get_worker_containers()

    assert len(workers) == 2

    device = create_device("worker-failover-device")

    wait_for_status(
        device["id"],
        "PROCESSING",
        timeout=10,
    )

    kill_container(workers[0])

    recovered_device = wait_for_status(
        device["id"],
        "READY",
        timeout=20,
    )

    assert recovered_device["status"] == "READY"
    assert recovered_device["processing_count"] == 2