from tests.framework.api_client import create_device
from tests.framework.db_client import get_device_from_db
from tests.framework.waiters import wait_for_status


def test_device_state_is_consistent_between_api_and_database():
    device = create_device("db-consistency-device")

    api_device = wait_for_status(
        device["id"],
        "READY",
        timeout=20,
    )

    db_device = get_device_from_db(device["id"])

    assert db_device is not None
    assert db_device["id"] == api_device["id"]
    assert db_device["status"] == api_device["status"]
    assert db_device["processing_count"] == api_device["processing_count"]