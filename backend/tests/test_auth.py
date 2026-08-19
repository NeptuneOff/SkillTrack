def test_register_and_login(client):
    response = client.post(
        "/auth/register",
        json={"email": "karl@example.com", "password": "StrongPassword123", "display_name": "Karl"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "karl@example.com"

    login = client.post("/auth/login", json={"email": "karl@example.com", "password": "StrongPassword123"})
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_duplicate_register_is_rejected(client):
    payload = {"email": "dupe@example.com", "password": "StrongPassword123", "display_name": "Karl"}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409
