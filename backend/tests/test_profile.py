def test_profile_requires_auth(client):
    response = client.get("/api/profile")
    assert response.status_code == 401, response.text


def test_profile_returns_current_user(client, registered_user, access_token):
    response = client.get(
        "/api/profile",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["email"] == registered_user["email"]
    assert data["full_name"] == registered_user["full_name"]
    assert "role" in data