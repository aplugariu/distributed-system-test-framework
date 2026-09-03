def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_read_device(client):
    create = client.post("/devices", json={"name": "radar-simulator"})
    assert create.status_code == 201
    body = create.json()
    assert body["name"] == "radar-simulator"
    assert body["status"] == "CREATED"

    read = client.get(f"/devices/{body['id']}")
    assert read.status_code == 200
    assert read.json()["id"] == body["id"]


def test_rejects_invalid_device_name(client):
    response = client.post("/devices", json={"name": "x"})
    assert response.status_code == 422


def test_unknown_device_returns_404(client):
    response = client.get("/devices/does-not-exist")
    assert response.status_code == 404
