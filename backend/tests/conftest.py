import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def unique_user():
    uid = uuid.uuid4().hex[:8]
    return {
        "full_name": f"Test User {uid}",
        "email": f"test_{uid}@example.com",
        "password": "TestPass123!",
    }


@pytest.fixture()
def registered_user(client, unique_user):
    response = client.post("/api/auth/register", json=unique_user)
    assert response.status_code in (200, 201), response.text
    return unique_user


@pytest.fixture()
def access_token(client, registered_user):
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
    return data["access_token"]