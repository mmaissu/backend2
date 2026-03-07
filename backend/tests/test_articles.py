"""Tests for articles CRUD and list (search, pagination)."""
import pytest
from httpx import AsyncClient


def _auth_headers(client: AsyncClient, email: str = "articles@example.com", password: str = "pass123") -> dict:
    """Register + login and return headers; assumes client has no state."""
    return {"Authorization": "Bearer fake-token-for-now"}  # Will override with real token in test


@pytest.mark.asyncio
async def test_list_articles_public(client: AsyncClient):
    """List is allowed without auth (read-only)."""
    r = await client.get("/api/articles?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert data["limit"] == 5


@pytest.mark.asyncio
async def test_create_article_requires_auth(client: AsyncClient):
    r = await client.post(
        "/api/articles",
        json={"title": "Test Article"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_and_get_article(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={"email": "author@example.com", "password": "pass123"},
    )
    login_r = await client.post(
        "/api/auth/login",
        json={"email": "author@example.com", "password": "pass123"},
    )
    token = login_r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_r = await client.post(
        "/api/articles",
        headers=headers,
        json={"title": "My Paper", "abstract": "Summary", "source": "Journal X"},
    )
    assert create_r.status_code == 201
    article = create_r.json()
    assert article["title"] == "My Paper"
    assert article["source"] == "Journal X"
    article_id = article["id"]

    get_r = await client.get(f"/api/articles/{article_id}")
    assert get_r.status_code == 200
    assert get_r.json()["title"] == "My Paper"
