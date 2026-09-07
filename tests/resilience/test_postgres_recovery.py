import httpx

from tests.framework.docker_control import kill_service, start_service
from tests.framework.waiters import wait_for_postgres, wait_for_status


BASE_URL = "http://localhost:8000"


def test_system_recovers_after_postgres_outage():
    kill_service("postgres")

    failed_response = httpx.post(
        f"{BASE_URL}/devices",
        json={"name": "postgres-down-device"},
        timeout=5,
    )

    assert failed_response.status_code >= 500

    start_service("postgres")

    wait_for_postgres(timeout=15)

    response = httpx.post(
        f"{BASE_URL}/devices",
        json={"name": "postgres-recovered-device"},
        timeout=5,
    )

    response.raise_for_status()

    recovered_device = wait_for_status(
        response.json()["id"],
        "READY",
        timeout=20,
    )

    assert recovered_device["status"] == "READY"