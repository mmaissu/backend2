"""Tests for auth: register, login, me."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    r = await client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "securepass123", "full_name": "Test User"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "user@example.com"
    assert data["role"] == "user"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={"email": "dup@example.com", "password": "securepass123"},
    )
    r = await client.post(
        "/api/auth/register",
        json={"email": "dup@example.com", "password": "otherpass"},
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={"email": "login@example.com", "password": "mypass123"},
    )
    r = await client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "mypass123"},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={"email": "wrong@example.com", "password": "correct"},
    )
    r = await client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": "wrong"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_unauthorized(client: AsyncClient):
    r = await client.get("/api/auth/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_authorized(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={"email": "me@example.com", "password": "pass123"},
    )
    login_r = await client.post(
        "/api/auth/login",
        json={"email": "me@example.com", "password": "pass123"},
    )
    token = login_r.json()["access_token"]
    r = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "me@example.com"
