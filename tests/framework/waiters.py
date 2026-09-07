import time

from tests.framework.api_client import get_device
from tests.framework.db_client import engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def wait_for_status(
    device_id: str,
    expected_status: str,
    timeout: float = 15.0,
) -> dict:
    deadline = time.time() + timeout

    while time.time() < deadline:
        device = get_device(device_id)

        if device["status"] == expected_status:
            return device

        time.sleep(0.25)

    raise AssertionError(
        f"Device {device_id} did not reach status {expected_status}"
    )

def wait_for_postgres(timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return

        except SQLAlchemyError:
            time.sleep(0.25)

    raise AssertionError(
        f"PostgreSQL did not become ready within {timeout}s"
    )