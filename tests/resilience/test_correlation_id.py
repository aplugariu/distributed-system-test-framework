import uuid
from tests.framework.logs import get_service_logs, get_trace
import httpx

from tests.framework.waiters import wait_for_status


BASE_URL = "http://localhost:8000"


def test_correlation_id_is_propagated_to_worker():
    correlation_id = f"corr-{uuid.uuid4().hex[:8]}"

    response = httpx.post(
        f"{BASE_URL}/devices",
        headers={
            "X-Correlation-ID": correlation_id,
        },
        json={
            "name": "correlation-id-test-device",
        },
        timeout=5,
    )

    response.raise_for_status()

    device_id = response.json()["id"]

    wait_for_status(
        device_id,
        "READY",
        timeout=20,
    )

    api_logs = get_service_logs("api")
    worker_logs = get_service_logs("worker")

    api_trace = get_trace(api_logs, correlation_id)
    worker_trace = get_trace(worker_logs, correlation_id)


    assert "service=api" in api_trace
    assert "event=job_queued" in api_trace

    assert "service=worker" in worker_trace
    assert "event=processing_started" in worker_trace
    assert "event=processing_completed" in worker_trace
    assert "status=PROCESSING" in worker_trace
    assert "status=READY" in worker_trace