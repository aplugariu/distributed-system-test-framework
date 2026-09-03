import httpx

BASE_URL = "http://localhost:8000"


def create_device(name: str) -> dict:
    response = httpx.post(
        f"{BASE_URL}/devices",
        json={"name": name},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def get_device(device_id: str) -> dict:
    response = httpx.get(
        f"{BASE_URL}/devices/{device_id}",
        timeout=5,
    )
    response.raise_for_status()
    return response.json()