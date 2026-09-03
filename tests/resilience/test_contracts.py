def test_api_error_contract_is_stable(client):
    response = client.get("/devices/not-found")
    payload = response.json()

    assert response.status_code == 404
    assert payload == {"detail": "Device not found"}
