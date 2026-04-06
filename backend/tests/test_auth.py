def test_register_user(client, unique_user):
    response = client.post("/api/auth/register", json=unique_user)

    assert response.status_code in (200, 201), response.text

    data = response.json()
    assert data["email"] == unique_user["email"]
    assert data["full_name"] == unique_user["full_name"]
    assert "id" in data


def test_login_returns_access_token(client, registered_user):
    response = client.post(
        "/api/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 10


def test_login_with_wrong_password_fails(client, registered_user):
    response = client.post(
        "/api/auth/login",
        json={
            "email": registered_user["email"],
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401, response.text