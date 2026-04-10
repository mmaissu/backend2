import os
import sys
import uuid
from pathlib import Path

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _get_test_database_url() -> str:
    """
    Tests require a real Postgres database because models use Postgres-specific
    types (UUID, JSONB).

    Configure via:
    - TEST_DATABASE_URL (required)
    """
    return os.getenv("TEST_DATABASE_URL") or ""


@pytest.fixture(scope="session")
def test_database_url() -> str:
    url = _get_test_database_url()
    if not url:
        pytest.skip("TEST_DATABASE_URL is not set; skipping DB-backed tests to avoid touching non-test DB.")
    return url


@pytest.fixture()
def engine(test_database_url: str):
    engine = create_async_engine(test_database_url, echo=False, pool_pre_ping=True)
    return engine


@pytest.fixture()
def sessionmaker(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def _prepare_database(engine):
    # Import inside fixture so env vars above can be set by the runner.
    from app.infrastructure.base import Base  # noqa: WPS433

    # Ensure connection works; skip cleanly if DB isn't reachable.
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"Database is not reachable for tests: {exc}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def db_session(sessionmaker):
    async with sessionmaker() as session:
        yield session


@pytest.fixture()
async def app(engine):
    # Create a fresh app and override DB dependency to use the test engine.
    from app.main import create_app  # noqa: WPS433
    from app.infrastructure.database import get_db  # noqa: WPS433

    app = create_app()

    async def _get_test_db():
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _get_test_db
    return app


@pytest.fixture()
async def async_client(app):
    # Don't re-raise app exceptions into the test process; assert on HTTP 500 instead.
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture()
def unique_user():
    uid = uuid.uuid4().hex[:8]
    return {
        "full_name": f"Test User {uid}",
        "email": f"test_{uid}@example.com",
        "password": "TestPass123!",
    }


@pytest.fixture()
async def registered_user(async_client, unique_user):
    response = await async_client.post("/api/auth/register", json=unique_user)
    assert response.status_code in (200, 201), response.text
    return unique_user


@pytest.fixture()
async def access_token(async_client, registered_user):
    response = await async_client.post(
        "/api/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    return data["access_token"]