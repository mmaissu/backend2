import pytest


@pytest.mark.asyncio
async def test_profile_requires_auth(async_client):
    response = await async_client.get("/api/profile")
    assert response.status_code == 401, response.text


@pytest.mark.asyncio
async def test_profile_returns_current_user(async_client, registered_user, access_token):
    response = await async_client.get(
        "/api/profile",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["email"] == registered_user["email"]
    assert data["full_name"] == registered_user["full_name"]
    assert "role" in data